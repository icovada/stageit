"""
Manage pure IOS network devices.

To be used with any Cisco device running old-style IOS
"""
import re
import logging
from libs.base_device import BaseDevice


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

    def _upgrade_to_bundle(self, uri):
        self._checksession()
        logging.info("Check file exists")

        flashuri = self.session._gen_full_path(uri.split("/")[-1])
        if not self.session._check_file_exists(flashuri):
            self.copy_file(uri)
        self._manage_stack(uri)
        logging.info("Upgrading IOS")
        confset = ["no boot system", "boot system {}".format(flashuri)]
        self.session.device.send_config_set(confset)
        self.session.device.send_command("wr\n\n\n\n\n\n\n")
        self.reload_device()
        return True

    def _manage_stack(self, uri):
        """Connect to device and issue copy command from uri."""
        logging.info('Copying from %s', uri)
        self._checksession()
        self.session.device.send_config_set(["file prompt quiet"])
        command = "copy " + uri + " flash:\n"
        # Destination filename [foo.bar]?
        self.session.device.write_channel(command)
        self.session.device.write_channel("\n")
        self.session.device.timeout = 1800  # Could take ages...
        out = self.session.device.read_until_prompt_or_pattern("Error")
        self.session.device.send_config_set(["no file prompt quiet"])
        if "Error" in out:
            self.session.close()
            raise ValueError("File transfer failed")
        elif "bytes copied" in out:
            return
