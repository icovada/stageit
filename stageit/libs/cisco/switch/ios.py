from stageit.libs.BaseDevice import BaseDevice
import re
import logging


class IOSSwitch(BaseDevice):

    def upgrade_software(self, uri, version = 'BUNDLE'):
        self.status = "Checking firmware version"
        logging.info(self.status)
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
        with self.driver(**self.sessiondata) as session:
            showver = session.device.send_command("show version")

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
        raise Exception("IOS does not have install mode. You should not have reached this")

    def _upgrade_to_bundle(self, uri):
        with self.driver(**self.sessiondata) as session:
            self.status = "Check file exists"
            logging.info(self.status)

            flashuri = session._gen_full_path(uri.split("/")[-1])
            if not session._check_file_exists(flashuri):
                self.copy_file(session, uri)

            self.status = "Upgrading IOS"
            logging.info(self.status)
            confset = ["no boot system", "boot system {}".format(flashuri)]
            session.device.send_config_set(confset)
            session.device.send_command("wr\n\n\n\n\n\n\n")
        self.reload_device()
        return True
