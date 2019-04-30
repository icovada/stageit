"""BaseDevice to be expanded by subclasses."""
import os
from io import BytesIO
import logging
from time import sleep
import napalm
import netmiko
from stageit.libs.db import History, newsession


class BaseDevice():
    """BaseDevice to be expanded by subclasses."""

    def __init__(self, hostname, port, transport, platform,
                 username, password, pkid, cservermgmt, **kwargs):
        """Define all class data."""
        self.status = 'Init'
        logging.info(self.status)
        self._has_connectivity = False
        try:
            assert username
            assert password
        except UnboundLocalError:
            username = ''
            password = ''

        self.driver = napalm.get_network_driver(platform)
        self.logbuffer = BytesIO()
        self.sessiondata = {'hostname': hostname,
                            'username': username,
                            'password': password,
                            'optional_args': {'port': port,
                                              'transport': transport,
                                              'session_log': self.logbuffer}}

        self.pkid = pkid
        self.cservermgmt = cservermgmt

        self.facts = None

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
                    self.cservermgmt.reset()

            else:
                raise IOError("Device unavailable")

    def getfacts(self):
        """Get device facts and update history db table."""
        self.status = 'Getting facts'
        logging.info(self.status)
        with self.driver(**self.sessiondata) as session:
            session.timeout = 10
            self.facts = session.get_facts()
        session = newsession()
        dbrow = session.query(History).get(self.pkid)
        dbrow.vendor = self.facts['vendor']
        dbrow.serial_number = self.facts['serial_number']
        dbrow.os_version = self.facts['os_version']
        dbrow.model = self.facts['model']
        session.commit()
        session.close()


    def load_temp_config(self, **kwargs):
        """
        Load temporary configuration to transfer files.

        Is called by upgrade_software if self._has_connectivity is False.
        """
        self.status = 'Loading temp config'
        logging.info(self.status)
        # Check if we have info from outside, otherwise default to dhcp
        if 'ip' not in kwargs or 'netmask' not in kwargs:
            kwargs['ip'] = 'dhcp'

        with self.driver(**self.sessiondata) as session:
            # Ignore warnings and worry later
            session.auto_rollback_on_error = False
            session.load_template(template_name="upgrade_template",
                                  template_path=os.path.abspath(
                                      os.path.curdir) + "/configs",
                                  username="cisco",
                                  password="cisco",
                                  l2_interface="Gi1/0/48",
                                  l3_interface="Vlan 1",
                                  vlan=1,
                                  ip="dhcp")
            session.commit_config()

            if kwargs['ip'] == 'dhcp':
                self.status = "Waiting for DHCP"
                logging.info(self.status)
                # Wait for device to grab ip.
                int_ip = {}
                while int_ip:
                    int_ip = session.get_interfaces_ip()

        self._has_connectivity = True

    def load_final_config(self, config, **values):
        """Load final configuration from template."""
        self.status = 'Loading final config'
        logging.info(self.status)
        with self.driver(**self.sessiondata) as session:
            session.load_template(template_source=config,
                                  template_name="stdin",
                                  **values)

            session.commit_config()

        self.save_config()

    def copy_file(self, session, uri):
        """Connect to device and issue copy command from uri."""
        self.status = 'Copying from {}'.format(uri)
        logging.info(self.status)
        session.device.send_config_set(["file prompt quiet"])
        command = "copy " + uri + " flash:\n"
        # Destination filename [foo.bar]?
        session.device.write_channel(command)
        session.device.write_channel("\n")
        session.device.timeout = 1800  # Could take ages...
        out = session.device.read_until_prompt_or_pattern("Error")
        session.device.send_config_set(["no file prompt quiet"])
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
        with self.driver(**self.sessiondata) as session:
            session.device.write_channel("wr\n")
            session.device.write_channel("\n\n\n")
            session.device.read_until_prompt()

    def reload_device(self):
        """Issue reload command."""
        self.status = 'Sending reload command'
        logging.info(self.status)
        with self.driver(**self.sessiondata) as session:
            session.device.write_channel("wr\n")
            session.device.write_channel("\n\n\n")
            session.device.read_until_prompt()
            session.device.write_channel("reload")
            session.device.write_channel("\n\n\n")
        self.checkavailable(1000)

    def close(self, logname=None):
        """Wrap-up task."""
        self.status = 'Saving log'
        logging.info(self.status)
        if logname is not None:
            with open(logname, "wb") as outlog:
                outlog.write(self.logbuffer.getvalue())
        else:
            return self.logbuffer.getvalue()
