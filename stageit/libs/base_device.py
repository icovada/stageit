"""BaseDevice to be expanded by subclasses."""
import os
import logging
from time import sleep
import napalm
import netmiko
import requests

URL_BASE = "http://web:8000/api/"
URL_SUFFIX = "/?format=json"


class BaseDevice():
    """BaseDevice to be expanded by subclasses."""

    def __init__(self, tserver, pkid, **kwargs):
        """Define all class data."""
        logging.info('Init')
        self._has_connectivity = False

        self.driver = napalm.get_network_driver(kwargs.get('platform'))
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
                logging.info('Waiting for device {}'.format(retries))
                try:
                    self.getfacts()
                except (netmiko.ssh_exception.NetMikoAuthenticationException, ValueError):
                    if retries > 100:
                        # Chill. Still booting.
                        sleep(10)
                except ConnectionRefusedError:
                    logging.info("Connection refused, resetting line")
                    self.tserver.reset()

            else:
                raise IOError("Device unavailable")

    def getfacts(self):
        """Get device facts and update history db table."""
        logging.info('Getting facts')
        self._checksession()
        self.facts = self.session.get_facts()

        data = {'vendor': self.facts['vendor'],
                'serial': self.facts['serial_number'],
                'os_version': self.facts['os_version'],
                'model': self.facts['model']}

        # Update history line with new facts we found
        requests.put(URL_BASE + 'history/' + self.pkid + URL_SUFFIX, data=data)
        logging.info('Getting facts done')

    def load_bootstrap_config(self, bootstraptemplate, values, **kwargs):
        """
        Load temporary configuration to transfer files.

        Is called by upgrade_software if self._has_connectivity is False.
        """

        logging.info('Loading temp config')
        self._checksession()

        # Ignore warnings and worry later
        self.session.auto_rollback_on_error = False
        self.session.load_template(template_source=bootstraptemplate,
                                   template_name="stdin",
                                   **values)
        self.session.commit_config()

        logging.info("Checking device got an IP")
        # Wait for device to grab ip.
        int_ip = {}
        while int_ip:
            int_ip = self.session.get_interfaces_ip()

        self.session.auto_rollback_on_error = True
        self._has_connectivity = True

    def load_final_config(self, config, **values):
        """Load final configuration from template."""
        logging.info('Loading final config')
        self._checksession()
        self.session.load_template(template_source=config,
                                   template_name="stdin",
                                   **values)

        self.session.commit_config()

        self.save_config()

    def copy_file(self, uri):
        """Connect to device and issue copy command from uri."""
        logging.info('Copying from {}'.format(uri))
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
            self.session.close()
            raise ValueError("File transfer failed")
        elif "bytes copied" in out:
            return

    def upgrade_software(self, uri, mode_install):
        """Not implemented."""
        self.session.close()
        raise NotImplementedError

    def getlog(self):
        """Return session log."""
        return self.logbuffer.getvalue().decode('utf-8')

    def save_config(self):
        """Issue write command."""
        logging.info('Saving config')
        self._checksession()
        self.session.device.write_channel("wr\n")
        self.session.device.write_channel("\n\n\n")
        self.session.device.read_until_prompt()

    def reload_device(self):
        """Issue reload command."""
        logging.info('Sending reload command')
        self._checksession()
        self.session.device.write_channel("wr\n")
        self.session.device.write_channel("\n\n\n")
        self.session.device.read_until_prompt()
        self.session.device.write_channel("reload")
        self.session.device.write_channel("\n\n\n")
        self.checkavailable(1000)

    def close(self, logname=None):
        """Wrap-up session."""
        self.session.close()

    def poststaging(self, commands):
        """Run commands after staging the device"""
        self._checksession()
        for line in commands.split("\n"):
            self.session.send_command(line)

    def _checksession(self):
        def _createsession():
                driver = self.driver(**self.sessiondata)
                try:
                    driver.open()
                except ConnectionRefusedError:
                    self.tserver.reset()
                return driver 

        # Cannot use session.is_alive) because it interacts weirdly
        # with out terminal server and makes the switch kill the connection
        if self.session is None: 
                self.session = _createsession()

        try:
            self.session._netmiko_device.timeout = 3
            self.session.get_users()
        except (OSError, AttributeError) as e:
            self.session = _createsession()
            
        self.session._netmiko_device.timeout = 60