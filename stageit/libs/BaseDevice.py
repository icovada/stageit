import napalm
import os
import netmiko
from io import BytesIO
import logging


class BaseDevice():
    def __init__(self, hostname, port, transport, platform, username, password, **kwargs):
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

    def checkavailable(self, retries):
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
                except (netmiko.ssh_exception.NetMikoAuthenticationException, ValueError) as e:
                    pass
            else:
                raise IOError("Device unavailable")

    def getfacts(self):
        self.status = 'Getting facts'
        logging.info(self.status)
        with self.driver(**self.sessiondata) as session:
            self.facts = session.get_facts()

    def load_temp_config(self, **kwargs):
        self.status = 'Loading temp config'
        logging.info(self.status)
        # Check if we have info from outside, otherwise default to dhcp
        if 'ip' not in kwargs or 'netmask' not in kwargs:
            kwargs['ip'] = 'dhcp'

        assert kwargs['username']
        assert kwargs['password']

        with self.driver(**self.sessiondata) as session:
            templateargs = kwargs.copy()
            # Ignore warnings and worry later
            session.auto_rollback_on_error = False
            session.load_template(template_name="upgrade_template",
                                  template_path=os.path.abspath(
                                      os.path.curdir) + "/configs",
                                  **templateargs)
            session.commit_config()

            # tempsessiondata = {'username': 'cisco',
            #                    'password': 'cisco'
            #                    }

            if kwargs['ip'] == 'dhcp':
                self.status = "Waiting for DHCP"
                logging.info(self.status)
                # Wait for device to grab ip.
                int_ip = {}
                while len(int_ip) == 0:
                    int_ip = session.get_interfaces_ip()

                # tempsessiondata['hostname'] = list(int_ip.keys())
            # else:
                # Value of 'ipv4' of the first interface in the dict. We should only have one for now anyway
            #     tempsessiondata['hostname'] = list(list(b.values())[0]['ipv4'].keys())[0]

        self._has_connectivity = True

    def load_final_config(self, config):
        self.status = 'Loading final config'
        logging.info(self.status)
        with self.driver(**self.sessiondata) as session:
            session.device.send_config_set(config)
        
        self.save_config()


    def copy_file(self, session, uri):
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

    def upgrade_software(self, version, uri, mode_install):
        raise NotImplementedError

    def getlog(self):
        return self.logbuffer.getvalue().decode('utf-8')

    def save_config(self):
        self.status = 'Saving config'
        logging.info(self.status)
        with self.driver(**self.sessiondata) as session:
            session.device.write_channel("wr\n")
            session.device.write_channel("\n\n\n")
            session.device.read_until_prompt()


    def reload_device(self):
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
        self.status = 'Saving log'
        logging.info(self.status)
        if logname is not None:
            with open(logname, "wb") as outlog:
                outlog.write(self.logbuffer.getvalue())
        else:
            return self.logbuffer.getvalue()
