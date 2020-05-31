"""Cisco Console Server class"""

import logging

from netmiko import Netmiko as netmiko
from libs.consoleserver import BaseConsoleServer


class CiscoConsoleServer(BaseConsoleServer):
    """Overload reset method for Cisco routers
    Tested on Cisco 1801"""

    def reset(self):
        """Connect and clear line"""
        devicetypemap = {'telnet': 'cisco_ios_telnet',
                         'ssh': 'cisco_ios'}
        logging.debug('Attempting to connect to terminal server')
        net_connect = netmiko(host=self.hostname,
                              username=self.username,
                              password=self.password,
                              device_type=devicetypemap[self.transport])
        logging.debug('Connection successful')

        cmd = "clear line {}".format(self.line)
        logging.debug('sending command %s', cmd)

        # send_command_timing as the router prompt != returned
        output = net_connect.send_command_timing(
            cmd, strip_command=False, strip_prompt=False)
        if "onfirm" in output:
            logging.debug('Received confirmation prompt, sending enter')
            net_connect.send_command_timing(
                "\n", strip_command=False, strip_prompt=False
            )
        logging.error('No confirmation prompt received, continue at own risk')

        net_connect.disconnect()
