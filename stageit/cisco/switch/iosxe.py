import stageit.BaseDevice
import re


class IOSXESwitch(stageit.BaseDevice.BaseDevice):
    def firmware_ok(self, firmware):
        with self.driver(**self.sessiondata) as session:
            showver = session.device.send_command("show version running")

            # This regex parses the following output
            # Switch Ports Model              SW Version        SW Image              Mode   
            # ------ ----- -----              ----------        ----------            ----   
            # *    1 28    WS-C3650-24PD      16.6.4            CAT3K_CAA-UNIVERSALK9 INSTALL
            #      2 52    WS-C3650-48PD      16.6.4            CAT3K_CAA-UNIVERSALK9 INSTALL

            verregex = r'^\* *(\d) (\d{1,2}) *([A-Za-z0-9\-]*) *([0-9\.]*) *([A-Za-z0-9\-_]*) (\w*)$'
            switches = re.findall(verregex, showver, re.MULTILINE)

            verdict = {}
            for member in switches:
                if firmware not in member:
                    return (False, member[3], member[5])

            return (True, member[3], member[5])

    def upgrade_software(self, uri, mode="install"):
        with self.driver(**self.sessiondata) as session:
            if mode == "install":
                self._upgrade_to_install(session, uri)
            else:
                self._upgrade_to_bundle(session, uri)

    def _upgrade_to_install(self, session, uri):
        command = "request platform software package install switch all file " + \
            uri + " force new auto-copy"
        session.device.timeout = 1800
        session.device.write_channel(command)
        output = session.device.read_until_prompt_or_pattern(
            r'\[y(es)?\/no?\]')
        if re.search(output, r'\[y(es)?\/no?\]', re.MULTILINE) is not None:
            # Answer yes to a prompt
            session.device.write_channel("y\n")
        session.device.read_until_prompt()

    def _upgrade_to_bundle(self, session, uri):
        confset = ["no boot system", "boot system "+ uri]
        session.device.send_config_set(confset)
        session.device.send_command("wr")
