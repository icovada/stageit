"""Use with IOS-XE switches such as 3650 and 3850."""
import re
import logging
from stageit.libs.base_device import BaseDevice


class IOSXESwitch(BaseDevice):
    """Expand BaseDevice with 3650- and 3850-specific commands."""

    def upgrade_software(self, uri, mode="INSTALL"):
        """Verify software version and if necessary upgrade through proper path."""
        logging.info("Checking firmware version")
        firmware = (False, None, None)
        if re.search(r'cat3k_caa-universalk9(?:ldpe)*\.(\d*\w*\.\d*\w*\.\d*\w*)\.', uri):
            # Catalyst 3650, 3750
            # cat3k_caa-universalk9.16.06.06.SPA.bin
            # cat3k_caa-universalk9ldpe.16.06.06.SPA.bin
            version = re.findall(
                r'cat3k_caa-universalk9(?:ldpe)*\.(\d*\w*\.\d*\w*\.\d*\w*)\.', uri)[0]

        else:
            self.session.close()
            raise Warning("Unsupported image file")

        while not firmware[0]:
            firmware = self._firmware_ok(version, mode)
            if not firmware[0]:
                if not self._has_connectivity:
                    raise ConnectionError("Cannot copy file, device has no IP")

                self._checksession()
                if self.facts['hostname'] == "Switch":
                    # hostname "Switch" breaks read_until_prompt with log:
                    # %IOSXE-5-PLATFORM: Switch 1 R0/0: Apr  8 12:28:31 packtool.sh: %INSTALL-5-OPERATION_COMPLETED_INFO: Completed expand package flash:cat3k_caa-universalk9.16.03.07.SPA.bin
                    self.session.load_merge_candidate(
                        config='hostname Upgrading')

                if mode == "BUNDLE":
                    upgradestatus = self._upgrade_to_bundle(uri)
                else:
                    upgradestatus = self._upgrade_to_install(uri)

            else:
                upgradestatus = True

            return upgradestatus

    def _firmware_ok(self, version, *args, **kwargs):
        # Strip leading zeroes from IOS version
        version = version.replace(".0", ".")
        self._checksession()
        showver = self.session.device.send_command("show version")

        # This regex parses the following output
        # Switch Ports Model              SW Version        SW Image              Mode
        # ------ ----- -----              ----------        ----------            ----
        # *    1 28    WS-C3650-24PD      16.6.4            CAT3K_CAA-UNIVERSALK9 INSTALL
        #      2 52    WS-C3650-48PD      16.6.4            CAT3K_CAA-UNIVERSALK9 INSTALL

        verregex = r'^\** *(\d) (\d{1,2}) *([A-Za-z0-9\-]*) *([0-9\.]*) *([A-Za-z0-9\-_]*) *(\w*)$'
        switches = re.findall(verregex, showver, re.MULTILINE)

        for member in switches:
            if version not in member:
                return (False, member[3], member[5])
            else:
                switchdata = member

        return (True, switchdata[3], switchdata[5])

    def _upgrade_to_install(self, uri):
        self._checksession()
        logging.info("Check file exists")

        flashuri = self.session._gen_full_path(uri.split("/")[-1])
        if not self.session._check_file_exists(flashuri):
            self.copy_file(uri)

        logging.info("Upgrading IOS XE to INSTALL mode")
        command = "request platform software package install switch all file {} force new auto-copy\n".format(
            flashuri)
        self.session.device.timeout = 1800
        self.session.device.write_channel(command)
        output = self.session.device.read_until_prompt_or_pattern(
            "SUCCESS: Finished install:")
        if " install failed in switch" in output:
            return False

        self.reload_device()
        return True

    def _upgrade_to_bundle(self, uri):
        self._checksession()
        logging.info("Check file exists")

        flashuri = self.session._gen_full_path(uri.split("/")[-1])
        if not self.session._check_file_exists(flashuri):
            self.copy_file(uri)

        logging.info("Upgrading IOS-XE to BUNDLE mode")
        confset = ["no boot system", "boot system {}".format(flashuri)]
        self.session.device.send_config_set(confset)
        self.session.device.send_command("wr\n\n\n\n\n\n\n")
        self.reload_device()
        return True
