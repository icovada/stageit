"""
Manage pure IOS network devices.

To be used with any Cisco device running old-style IOS
"""
import re
import logging
from stageit.libs.base_device import BaseDevice


class IOSSwitch(BaseDevice):
    """Manage pure IOS devices"""

    def upgrade_software(self, uri, **kwargs):
        """Upgrade device firmware. IOS only supports BUNDLE mode."""
        logging.info("Checking firmware version")
        firmware = (False, None, None)
        version = uri.split("/")[-1]

        while not firmware[0]:
            firmware = self._firmware_ok(version)
            if not firmware[0]:
                if not self._has_connectivity:
                    raise ConnectionError("Cannot copy file, device has no IP")

                upgradestatus = self._upgrade_to_bundle(uri)

            else:
                upgradestatus = True

            return upgradestatus

    def _firmware_ok(self, version):
        self._checksession()
        showver = self.session.device.send_command("show version")

        # This regex parses the following output
        # System image file is "flash:c2960x-universalk9-mz.152-2.E5.bin"
        # System image file is "flash:/c3560cx-universalk9-mz.152-4.E6/c3560cx-universalk9-mz.152-4.E6.bin"

        verregex = r'image file is "\w*\:\/*(?:.*\/)*(.*)"'
        curversion = re.findall(verregex, showver, re.MULTILINE)[0]

        if curversion == version:
            return (True, curversion, "BUNDLE")
        else:
            return (False, curversion, "BUNDLE")

    def _upgrade_to_install(self, uri):
        raise Exception(
            "IOS does not have install mode. You should not have reached this")

    def _upgrade_to_bundle(self, uri):
        self._checksession()
        logging.info("Check file exists")

        flashuri = self.session._gen_full_path(uri.split("/")[-1])
        if not self.session._check_file_exists(flashuri):
            self.copy_file(uri)

        logging.info("Upgrading IOS")
        confset = ["no boot system", "boot system {}".format(flashuri)]
        self.session.device.send_config_set(confset)
        self.session.device.send_command("wr\n\n\n\n\n\n\n")
        self.reload_device()
        return True
