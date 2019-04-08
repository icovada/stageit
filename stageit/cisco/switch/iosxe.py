import stageit.BaseDevice
import re


class IOSXESwitch(stageit.BaseDevice.BaseDevice):
    def firmware_ok(self, firmware):
        with self.driver(**self.sessiondata) as session:
            showver = session.device.send_command("show version")

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
            if session.facts['hostname'] == "Switch":
                # hostname "Switch" breaks read_until_prompt with log:
                # %IOSXE-5-PLATFORM: Switch 1 R0/0: Apr  8 12:28:31 packtool.sh: %INSTALL-5-OPERATION_COMPLETED_INFO: Completed expand package flash:cat3k_caa-universalk9.16.03.07.SPA.bin
                session.device.send_config_set(["hostname Upgrading"])
            
            if mode == "install":
                upgradestatus = self._upgrade_to_install(session, uri)
            else:
                upgradestatus = self._upgrade_to_bundle(session, uri)
            
            session.device.send_config_set(["hostname "+session.facts['hostname']])
            return upgradestatus

    def _upgrade_to_install(self, session, uri):
        command = "request platform software package install switch all file " + \
            uri + " force new auto-copy\n"
        session.device.timeout = 1800
        session.device.write_channel(command)
        output = session.device.read_until_prompt_or_pattern(
            r'\[y(es)?\/no?\]')
        if re.search(output, r'\[y(es)?\/no?\]', re.MULTILINE) is not None:
            # Answer yes to a prompt
            session.device.write_channel("y\n")
        output = session.device.read_until_prompt_or_pattern("SUCCESS: Finished install:")
        if "SUCCESS: Finished install:" in output:
            return True
        else:
            return False


    def _upgrade_to_bundle(self, session, uri):
        confset = ["no boot system", "boot system "+ uri]
        session.device.send_config_set(confset)
        session.device.send_command("wr")
        return True
