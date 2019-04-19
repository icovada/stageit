from stageit.libs.BaseDevice import BaseDevice
import re
import logging


class IOSXESwitch(BaseDevice):

    def upgrade_software(self, uri, mode="INSTALL"):
        self.status = "Checking firmware version"
        logging.info(self.status)
        firmware = (False, None, None)
        try:
            version = re.findall(
                r'cat3k_caa-universalk9(?:ldpe)*\.(\d*\w*\.\d*\w*\.\d*\w*)\.', uri)[0]
        except IndexError:
            raise Warning("Unsupported image file")

        while not firmware[0]:
            firmware = self._firmware_ok(version, mode)
            if not firmware[0]:
                if not self._has_connectivity:
                    raise ConnectionError("Cannot copy file, device has no IP")

                with self.driver(**self.sessiondata) as session:
                    if self.facts['hostname'] == "Switch":
                        # hostname "Switch" breaks read_until_prompt with log:
                        # %IOSXE-5-PLATFORM: Switch 1 R0/0: Apr  8 12:28:31 packtool.sh: %INSTALL-5-OPERATION_COMPLETED_INFO: Completed expand package flash:cat3k_caa-universalk9.16.03.07.SPA.bin
                        session.load_merge_candidate(
                            config='hostname Upgrading')

                if mode == "BUNDLE":
                    upgradestatus = self._upgrade_to_bundle(uri)
                else:
                    upgradestatus = self._upgrade_to_install(uri)

            else:
                upgradestatus = True

            return upgradestatus

    def _firmware_ok(self, version, mode='INSTALL'):
        # Strip leading zeroes from IOS version
        version = version.replace(".0", ".")
        with self.driver(**self.sessiondata) as session:
            showver = session.device.send_command("show version")

            # This regex parses the following output
            # Switch Ports Model              SW Version        SW Image              Mode
            # ------ ----- -----              ----------        ----------            ----
            # *    1 28    WS-C3650-24PD      16.6.4            CAT3K_CAA-UNIVERSALK9 INSTALL
            #      2 52    WS-C3650-48PD      16.6.4            CAT3K_CAA-UNIVERSALK9 INSTALL

            verregex = r'^\** *(\d) (\d{1,2}) *([A-Za-z0-9\-]*) *([0-9\.]*) *([A-Za-z0-9\-_]*) (\w*)$'
            switches = re.findall(verregex, showver, re.MULTILINE)

            for member in switches:
                if version not in member:
                    return (False, member[3], member[5])

            return (True, member[3], member[5])

    def _upgrade_to_install(self, uri):
        with self.driver(**self.sessiondata) as session:
            self.status = "Check file exists"
            logging.info(self.status)

            flashuri = session._gen_full_path(uri.split("/")[-1])
            if not session._check_file_exists(flashuri):
                self.copy_file(session, uri)

            self.status = "Upgrading IOS XE to INSTALL mode"
            logging.info(self.status)
            command = "request platform software package install switch all file {} force new auto-copy\n".format(
                flashuri)
            session.device.timeout = 1800
            session.device.write_channel(command)
            output = session.device.read_until_prompt_or_pattern(
                "SUCCESS: Finished install:")
            if " install failed in switch" in output:
                return False

        self.reload_device()
        return True

    def _upgrade_to_bundle(self, uri):
        with self.driver(**self.sessiondata) as session:
            self.status = "Check file exists"
            logging.info(self.status)

            flashuri = session._gen_full_path(uri.split("/")[-1])
            if not session._check_file_exists(flashuri):
                self.copy_file(session, uri)

            self.status = "Upgrading IOS-XE to BUNDLE mode"
            logging.info(self.status)
            confset = ["no boot system", "boot system {}".format(flashuri)]
            session.device.send_config_set(confset)
            session.device.send_command("wr\n\n\n\n\n\n\n")
        self.reload_device()
        return True
