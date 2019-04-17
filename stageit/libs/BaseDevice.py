import napalm
import os
import netmiko
from io import BytesIO


class BaseDevice():
    def __init__(self, hostname, port, transport, vendor, username, password, **kwargs):
        self.status = 'Init'
        self._has_connectivity = False
        try:
            assert username
            assert password
        except UnboundLocalError:
            username = ''
            password = ''

        self.driver = napalm.get_network_driver(vendor)
        self.logbuffer = BytesIO()
        self.sessiondata = {'hostname': hostname,
                            'username': username,
                            'password': password,
                            'optional_args': {'port': port,
                                              'transport': transport,
                                              'session_log': self.logbuffer}}

    def checkavailable(self, retries):
        self.status = 'Waiting for connection'
        self.facts = None
        while self.facts is None:
            if retries >= 0:
                retries = retries - 1
                self.status = 'Waiting for device {}'.format(retries)
                try:
                    self.getfacts()
                except netmiko.ssh_exception.NetMikoAuthenticationException:
                    self.status = 'Failed to connect'
                    pass
            else:
                raise IOError("Device unavailable")

    def getfacts(self):
        self.status = 'Getting facts'
        with self.driver(**self.sessiondata) as session:
            self.facts = session.get_facts()

    def load_temp_config(self, **kwargs):
        self.status = 'Loading temp config'
        # Check if we have info from outside, otherwise default to dhcp
        if 'ip' not in kwargs or 'netmask' not in kwargs:
            kwargs['ip'] = 'dhcp'

        assert kwargs['username']
        assert kwargs['password']

        with self.driver(**self.sessiondata) as session:
            templateargs = kwargs.copy()
            del templateargs['template_name']
            session.load_template(template_name="upgrade_template",
                                  template_path=os.path.abspath(
                                  os.path.curdir) + "/configs",
                                  **templateargs)
            session.commit_config()

            tempsessiondata = {'username': 'cisco',
                               'password': 'cisco'
                               }

            if kwargs['ip'] == 'dhcp':
                # Wait for device to grab ip.
                session.device.timeout = 60
                session.device.read_until_pattern("DHCP")
                showint = session.get_interfaces_ip()
                tempsessiondata['hostname'] = showint[kwargs['l3_interface']]['ipv4'].popitem()[
                    0]
            else:
                tempsessiondata['hostname'] = kwargs['ip']
        self._has_connectivity = True

    def load_final_config(self, template, **kwargs):
        self.status = 'Loading final config'
        with self.driver(**self.sessiondata) as session:
            session.load_template(template_name=template,
                                  template_path=os.path.abspath(
                                      os.path.curdir) + "/configs",
                                  **kwargs)

    def copy_file(self, uri):
        self.status = 'Copying from {}'.format(uri)
        with self.driver(**self.sessiondata) as session:
            session.device.send_config_set(["file prompt quiet"])
            command = "copy " + uri + " flash:\n"
            session.device.write_channel(command)
            session.device.read_until_pattern(r"\?")
            # Destination filename [foo.bar]?
            session.device.write_channel("\n")
            session.device.timeout = 1800  # Could take ages...
            out = session.device.read_until_prompt_or_pattern("Error")
            session.device.send_config_set(["no file prompt quiet"])
            if "Error" in out:
                raise ValueError("File transfer failed")
            elif "OK" in out:
                return

    def upgrade_software(self, version, uri, mode_install):
        raise NotImplementedError

    def getbuffer(self):
        return self.logbuffer.getvalue()

    def reload(self):
        self.status = 'Sending reload command'
        with self.driver(**self.sessiondata) as session:
            session.device.send_command("wr\n")
            session.device.send_command("\n\n\n")
            session.device.read_until_prompt()
            session.device.send_command("reload")
            session.device.send_command("\n\n\n")
            self.checkavailable(1000)

    def close(self, logname=None):
        self.status = 'Saving log'
        if logname is not None:
            with open(logname, "wb") as outlog:
                outlog.write(self.logbuffer.getvalue())
        else:
            return self.logbuffer.getvalue()
