"""BaseDevice to be expanded by subclasses."""
import logging
from time import sleep

import napalm
import netmiko
import requests
from napalm.base.exceptions import ConnectionClosedException
from netmiko.ssh_exception import NetMikoAuthenticationException

URL_SUFFIX = "/?format=json"


class BaseDevice():
    """BaseDevice to be expanded by subclasses."""

    def __init__(self, tserver, endpoint, pkid, headers, **kwargs):
        """Define all class data."""
        logging.info('Init')
        self._has_connectivity = False

        self.driver = napalm.get_network_driver('ios')
        self.logbuffer = kwargs.get('logbuffer')
        self.sessiondata = {'hostname': kwargs.get('hostname'),
                            'username': kwargs.get('username'),
                            'password': kwargs.get('password'),
                            'optional_args': {'port': kwargs.get('port'),
                                              'transport': kwargs.get('transport'),
                                              'session_log': kwargs.get('logbuffer'),
                                              'secret': 'cisco'}}
        self.session = None
        self.tserver = tserver
        self.endpoint = endpoint
        self.headers = headers

        self._checksession()

        self.facts = None
        self.pkid = pkid

    def checkavailable(self, retries):
        """Check if device is available and has booted."""
        logging.info('Waiting for connection')
        self.facts = None

        # Repeat until we get data from the device
        while self.facts is None:
            if retries >= 0:
                retries = retries - 1
                logging.info('Waiting for device, %s more tries before failure', retries)
                try:
                    # TODO: Try a less invasive command, getfacts takes ages
                    self.getfacts()
                except (netmiko.ssh_exception.NetMikoAuthenticationException, ValueError, AttributeError):
                    if retries > 100:
                        # Chill. Still booting.
                        sleep(10)
                except ConnectionRefusedError:
                    logging.warning('Connection refused, resetting line')
                    self.tserver.reset()

            else:
                logging.error("Device unavailable")
                raise IOError("Device unavailable")

    def getfacts(self):
        """Get device facts and update history db table."""
        logging.info('Getting facts')
        self._checksession()
        self.facts = self.session.get_facts()
        logging.debug('Session facts: %s', self.facts)

        data = {'vendor': self.facts['vendor'],
                'serial': self.facts['serial_number'],
                'os_version': self.facts['os_version'],
                'model': self.facts['model']}

        # Update history line with new facts we found
        # TODO: Manage network error
        url = self.endpoint + '/api/history/' + self.pkid + URL_SUFFIX
        logging.debug('PUT %s, data: %s', url, data)
        requests.put(url, data=data, headers=self.headers)
        logging.debug('Successful history update')
        logging.info('Getting facts done')

    def load_bootstrap_config(self, bootstraptemplate, values, **kwargs):
        """
        Load temporary configuration to transfer files.

        Is called before upgrade_software if automatic DHCP has failed
        """

        logging.info('Loading temp config')
        self._checksession()

        # Ignore warnings and worry later
        self.session.auto_rollback_on_error = False
        self.session.load_template(template_source=bootstraptemplate,
                                   template_name="stdin",
                                   **values)
        self.session.commit_config()
        logging.info('Loaded bootstrap config')

        logging.info("Checking device has an IP")
        # Wait for device to grab ip.
        int_ip = {}
        while True not in ["ipv4" in x for x in int_ip.values()]:
            logging.info('Checking again if device has IP')
            # While there are no interfaces with an 'ipv4' address type
            int_ip = self.session.get_interfaces_ip()
        logging.info('Device acquired IP')
        logging.debug(int_ip)

        self.session.auto_rollback_on_error = True
        self._has_connectivity = True

    def load_final_config(self, config, **values):
        """Load final configuration from template."""
        logging.info('Loading final config')
        self._checksession()
        self.session.load_template(template_source=config,
                                   template_name="stdin",
                                   **values)

        logging.info('Loaded final config')
        self.session.commit_config()

        self.save_config()

    def copy_file(self, uri):
        """Connect to device and issue copy command from uri."""
        logging.info('Copying from %s', uri)
        self._checksession()
        self.session.device.send_config_set(["file prompt quiet"])
        command = "copy " + uri + " flash:\n"
        # Destination filename [foo.bar]?
        self.session.device.write_channel(command)
        self.session.device.write_channel("\n")
        self.session.device.timeout = 1800  # Could take ages...
        out = self.session.device.read_until_prompt_or_pattern("Error")
        self.session.device.send_config_set(["no file prompt quiet"])
        if "Error" in out:
            logging.error('File failed to copy')
            self.session.close()
            raise ValueError("File transfer failed")
        elif "bytes copied" in out:
            logging.info('File copy complete')
            return

    def upgrade_software(self, **kwargs):
        """Not implemented."""
        logging.error('Called base_device.upgrade_software, which is undefined')
        self.session.close()
        raise NotImplementedError

    def getlog(self):
        """Return session log."""
        return self.logbuffer.getvalue().decode('utf-8')

    def save_config(self):
        """Issue write command."""
        logging.info('Saving config')
        self._checksession()
        logging.debug('Sending wr\\n\\n\\n\\n')
        self.session.device.write_channel("wr\n")
        self.session.device.write_channel("\n\n\n")
        logging.debug('Waiting for prompt')
        self.session.device.read_until_prompt()
        logging.debug('Save config complete')

    def reload_device(self):
        """Issue reload command."""
        logging.info('Sending reload command')
        self.save_config()
        logging.debug('Sending reload\\n\\n\\n')
        self.session.device.write_channel("reload")
        self.session.device.write_channel("\n\n\n")
        self.session.device.timeout = 900   # 15 minutes of reboot time is not unheard of
        logging.debug('Reload sent, waiting for reboot')
        self.session.device.read_until_prompt_or_pattern('Press RETURN to get started')
        self.checkavailable(20)

    def close(self):
        """Wrap-up session."""
        self.session.close()

    def poststaging(self, commands):
        """Run commands after staging the device"""
        self._checksession()
        logging.info('Starting post-staging phase')
        for line in commands.split("\n"):
            logging.debug('Sending command %s', line)
            self.session.device.send_command(line)

    def _checksession(self):
        def _createsession():
            logging.debug('Creating new driver')
            driver = self.driver(**self.sessiondata)
            try:
                logging.debug('Opening new connection')
                driver.open()
                driver.device.send_command("ter len 0\n")
            except (ConnectionRefusedError, NetMikoAuthenticationException):
                logging.warning('Connection failed, resetting terminal server')
                self.tserver.reset()
            return driver

        # Cannot use session.is_alive()) because it interacts weirdly
        # with our terminal server and makes the switch kill the connection
        if self.session is None:
            logging.warning('Session dead, creating new one')
            self.session = _createsession()

        try:
            logging.debug('Running test command on session')
            self.session._netmiko_device.timeout = 3
            self.session.get_users()
        except (OSError, AttributeError, ConnectionClosedException) as e:
            logging.warning('Session dead, creating new one')
            self.session = _createsession()

        try:
            self.session._netmiko_device.timeout = 60
        except (OSError, AttributeError, ConnectionClosedException) as e:
            logging.warning('Session dead, creating new one')
            self.session = _createsession()
