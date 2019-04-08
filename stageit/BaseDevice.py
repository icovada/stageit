import napalm
import os
import netmiko
from io import BytesIO


class BaseDevice():
    def __init__(self, hostname, port, transport, vendor, username, password, retries=5):
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

        self.facts = None
        while self.facts is None:
            if retries >= 0:
                retries = retries
                    with self.driver(**self.sessiondata) as session:
                        self.facts = session.get_facts()
                except netmiko.ssh_exception.NetMikoAuthenticationException:
                    pass
            else:
                raise "SerialAuthenticationException"

    def load_temp_config(self, **kwargs):
        # Check if we have info from outside, otherwise default to dhcp
        if 'ip' not in kwargs or 'netmask' not in kwargs:
            kwargs['ip'] = 'dhcp'

        assert kwargs['username']
        assert kwargs['password']

        with self.driver(**self.sessiondata) as session:
            session.load_template(template_name="upgrade_template",
                                  template_path=os.path.abspath(
                                      os.path.curdir) + "/configs",
                                  **kwargs)
            session.commit_config()

            tempsessiondata = {'username': 'cisco',
                               'password': 'cisco'
                               }

            if kwargs['ip'] == 'dhcp':
                # Wait for device to grab ip.
                session.device.read_until_pattern("DHCP")
                showint = session.get_interfaces_ip()
                tempsessiondata['hostname'] = showint[kwargs['l3_interface']]['ipv4'].popitem()[0]
            else:
                tempsessiondata['hostname'] = kwargs['ip']

        return tempsessiondata

    def load_final_config(self, template, **kwargs):
        with self.driver(**self.sessiondata) as session:
            session.load_template(template_name=template,
                                  template_path=os.path.abspath(
                                      os.path.curdir) + "/configs",
                                  **kwargs)

    def copy_from_ftp(self, uri):
        with self.driver(**self.sessiondata) as session:
            command = "copy " + uri + "flash:"
            session.device.write_channel(command)
            session.device.read_until_pattern("\?")
            # Destination filename [foo.bar]?
            session.device.write_channel("\n")
            session.device.timeout = 1800 # Could take ages...
            out = session.device.read_until_prompt_or_pattern("Error"
            if "Error" in out:
                raise ValueError("File transfer failed")
            else if "OK" in out:
                return

    def upgrade_software(self, software, sessiondata=None, pkgexpand=False):
        raise NotImplementedError

    def getbuffer(self):
        return self.logbuffer.getvalue()

    def reload(self):
        with self.driver(**self.sessiondata) as session:
            session.device.send_command("reload")
            session.device.send_command("y\n")

    def close(self, logname=None):
        if logname is not None:
            with open(logname, "wb") as outlog:
                outlog.write(self.logbuffer.getvalue())
        else:
            return self.logbuffer.getvalue()
