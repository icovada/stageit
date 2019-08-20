"""BaseDevice to be expanded by subclasses."""
import os
import logging
from time import sleep
import napalm
import netmiko
import requests

URL_BASE = "http://localhost:8000/api/"
URL_SUFFIX = "/?format=json"


class BaseDevice():
    """BaseDevice to be expanded by subclasses."""

    def __init__(self, tserver, pkid, **kwargs):
        """Define all class data."""
        self.status = 'Init'
        logging.info(self.status)
        self._has_connectivity = False

        self.driver = napalm.get_network_driver(kwargs.get('platform'))
        self.logbuffer = kwargs.get('logbuffer')
        self.sessiondata = {'hostname': kwargs.get('hostname'),
                            'username': kwargs.get('username'),
                            'password': kwargs.get('password'),
                            'optional_args': {'port': kwargs.get('port'),
                                              'transport': kwargs.get('transport'),
                                              'session_log': kwargs.get('logbuffer')}}
        self.session = None
        self._checksession()

        self.tserver = tserver

        self.facts = None
        self.pkid = pkid

    def checkavailable(self, retries):
        """Check if device is available and has booted."""
        self.status = 'Waiting for connection'
        logging.info(self.status)
        self.facts = None
        while self.facts is None:
            if retries >= 0:
                retries = retries - 1
                self.status = 'Waiting for device {}'.format(retries)
                logging.info(self.status)
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
        self.status = 'Getting facts'
        logging.info(self.status)
        self._checksession()
        #oldtimeout = self.session.timeout
        #self.session.timeout = 10
        self._checksession()
        self.session.open()
        self.facts = self.session.get_facts()
        #self.session.timeout = oldtimeout

        data = {'vendor': self.facts['vendor'],
                'serial': self.facts['serial_number'],
                'os_version': self.facts['os_version'],
                'model': self.facts['model']}
        requests.put(URL_BASE + 'history/' + self.pkid + URL_SUFFIX, data=data)

    def load_temp_config(self, **kwargs):
        """
        Load temporary configuration to transfer files.

        Is called by upgrade_software if self._has_connectivity is False.
        """
        self.status = 'Loading temp config'
        logging.info(self.status)
        self._checksession()
        # Check if we have info from outside, otherwise default to dhcp
        if 'ip' not in kwargs or 'netmask' not in kwargs:
            kwargs['ip'] = 'dhcp'

        # Ignore warnings and worry later
        self.session.auto_rollback_on_error = False
        self.session.load_template(template_name="upgrade_template",
                                   template_path=os.path.abspath(
                                       os.path.curdir) + "/configs",
                                   username="cisco",
                                   password="cisco",
                                   l2_interface="Gi1/0/48",
                                   l3_interface="Vlan 1",
                                   vlan=1,
                                   ip="dhcp")
        self.session.commit_config()

        if kwargs['ip'] == 'dhcp':
            self.status = "Waiting for DHCP"
            logging.info(self.status)
            # Wait for device to grab ip.
            int_ip = {}
            while int_ip:
                int_ip = self.session.get_interfaces_ip()

        self.session.auto_rollback_on_error = True
        self._has_connectivity = True

    def load_final_config(self, config, **values):
        """Load final configuration from template."""
        self.status = 'Loading final config'
        logging.info(self.status)
        self._checksession()
        self.session.load_template(template_source=config,
                                   template_name="stdin",
                                   **values)

        self.session.commit_config()

        self.save_config()

    def copy_file(self, uri):
        """Connect to device and issue copy command from uri."""
        self.status = 'Copying from {}'.format(uri)
        logging.info(self.status)
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
            raise ValueError("File transfer failed")
        elif "bytes copied" in out:
            return

    def upgrade_software(self, uri, mode_install):
        """Not implemented."""
        raise NotImplementedError

    def getlog(self):
        """Return session log."""
        return self.logbuffer.getvalue().decode('utf-8')

    def save_config(self):
        """Issue write command."""
        self.status = 'Saving config'
        logging.info(self.status)
        self._checksession()
        self.session.device.write_channel("wr\n")
        self.session.device.write_channel("\n\n\n")
        self.session.device.read_until_prompt()

    def reload_device(self):
        """Issue reload command."""
        self.status = 'Sending reload command'
        logging.info(self.status)
        self._checksession()
        self.session.device.write_channel("wr\n")
        self.session.device.write_channel("\n\n\n")
        self.session.device.read_until_prompt()
        self.session.device.write_channel("reload")
        self.session.device.write_channel("\n\n\n")
        self.checkavailable(1000)

    def close(self, logname=None):
        """Wrap-up task."""
        self.session.close()

    def _checksession(self):
        def _createsession():
                driver = self.driver(**self.sessiondata)
                driver.open()
                return driver 

        if self.session is None or not self.session.is_alive().get('is_alive'):
                self.session = _createsession()
