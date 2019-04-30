from stageit.libs.consoleserver import BaseConsoleServer
from netmiko import Netmiko as netmiko

class CiscoConsoleServer(BaseConsoleServer):
    def reset(self):
        devicetypemap = {'telnet': 'cisco_ios_telnet',
                         'ssh': 'cisco_ios'}
        net_connect = netmiko(host=self.hostname,
                              username=self.username,
                              password=self.password,
                              device_type=devicetypemap[self.transport])

        cmd = "clear line {}".format(self.line)

        # send_command_timing as the router prompt is not returned
        output = net_connect.send_command_timing(
            cmd, strip_command=False, strip_prompt=False)
        if "onfirm" in output:
            net_connect.send_command_timing(
                "\n", strip_command=False, strip_prompt=False
            )

        net_connect.disconnect()
