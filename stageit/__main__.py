import napalm
import netmiko
import yaml
import jinja2
import os
from time import sleep


class device():
    def __init__(self, hostname, port, transport, vendor, username, password):
        try:
            assert username
            assert password
        except UnboundLocalError:
            username = ''
            password = ''

        self.driver = napalm.get_network_driver(vendor)
        self.sessiondata = {'hostname': hostname,
                            'username': username,
                            'password': password,
                            'optional_args': {'port': port,
                                              'transport': transport}}

        with self.driver(**self.sessiondata) as session:
            self.facts = session.get_facts()

    def firmware_ok(self, version):
        with self.driver(**self.sessiondata) as session:
            shver = session.device.send_command("show ver")
            if version in shver:
                return True

    def load_temp_config(self, **kwargs):
        # Check if we have info from outside, otherwise default to dhcp
        if 'ip' not in kwargs or 'netmask' not in kwargs:
            kwargs['ip'] = 'dhcp'
        
        assert kwargs['username']
        assert kwargs['password']

        with self.driver(**self.sessiondata) as session:
            intlist = session.get_interfaces()
            if 'l3_interface' in kwargs:
                assert kwargs['l3_interface'] in intlist or "lan" in kwargs['l3_interface']
            if 'l2_interface' in kwargs:
                assert kwargs['l2_interface'] in intlist
            session.load_template(template_name="upgrade_template",
                                  template_path=os.path.abspath(os.path.curdir) + "/configs",
                                  **kwargs)
            session.commit_config()

            tempsessiondata = {'username': 'cisco',
                               'password': 'cisco'
                              }

            if kwargs['ip'] == 'dhcp':
                pass
                # Wait for device to grab ip. TODO: Asynchronicity
                #sleep(10)
                #showint = session.get_interfaces_ip()
                #tempsessiondata['hostname'] = showint[kwargs['l3_interface']]['ipv4'].popitem()[0]
            else:
                tempsessiondata['hostname'] = kwargs['ip']

        return tempsessiondata

    def upgrade_software(self, software, sessiondata):
        with self.driver(**sessiondata) as session:
            upgradefacts = session.get_facts()
            if upgradefacts['serial_number'] != self.facts['serial_number']:
                raise WrongDeviceError
            scpresult = session._scp_file(software, software, session.dest_file_system)
            if scpresult[0] is not True:
                raise FileNotCopiedError
            
            bootvar = session.device.send_command("show bootvar")
            if "Invalid input" in bootvar:
                upgradepath = "boot system " + session.dest_file_system + "/"
                session.load_merge_candidate(config=upgradepath)
            else:
                # TODO erase bootvar
                pass

            session.commit_config()


if __name__ == '__main__':
    config = yaml.load('term_config.yaml')

    d = device("127.0.0.1", 5007, 'telnet', 'ios', 'cisco', 'cisco')