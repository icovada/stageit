"""Use with IOS-XE switches such as 3650 and 3850."""
import re
import logging
from stageit.libs.base_device import BaseDevice


class IOSXELiteSwitch(BaseDevice):
    """Expand BaseDevice with IOS-XE_Lite-specific commands."""

    def upgrade_software(self, uri, mode="INSTALL"):
        """Verify software version and if necessary upgrade through proper path."""
        logging.info("Checking firmware version")
        firmware = (False, None, None)
        if re.search(r'cat9k_lite_iosxe(_npe)?(\.(\d{2})){3}\.SPA\.bin', uri):
            # Catalyst 9200
            # cat3k_caa-universalk9.16.06.06.SPA.bin
            # cat3k_caa-universalk9ldpe.16.06.06.SPA.bin
            version = re.findall(
                r'cat9k_lite_iosxe(_npe)?(\.(\d{2})){3}\.SPA\.bin', uri)[0]

        if re.search(r'cat9k_lite_iosxe(_npe)?(\.(\d{2})){3}\.SPA\.bin', uri):
            # Catalyst 9200, 9300
            # cat9k_lite_iosxe.16.12.01.SPA.bin
            # cat9k_lite_iosxe_npe.16.12.01.SPA.bin
            version = re.findall(
                r'cat9k_lite_iosxe(_npe)?(\.(\d{2})){3}\.SPA\.bin', uri)[0]
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

                # No support for bundle mode on ios-xe-lite
                upgradestatus = self._upgrade_to_install(uri)

            else:
                upgradestatus = True

            return upgradestatus

    def _firmware_ok(self, version, mode='INSTALL'):
        # Strip leading zeroes from IOS version
        version = version.replace(".0", ".")
        self._checksession()
        showver = self.session.device.send_command("show version")

        # This regex parses the following output
        # Switch Ports Model              SW Version        SW Image              Mode   
        # ------ ----- -----              ----------        ----------            ----   
        # *    1 52    C9200L-48P-4G      16.12.1           CAT9K_LITE_IOSXE      INSTALL
        #      2 52    C9200L-48P-4G      16.12.1           CAT9K_LITE_IOSXE      INSTALL
        #      3 52    C9200L-48P-4G      16.12.1           CAT9K_LITE_IOSXE      INSTALL


        verregex = r'^\** *(\d) (\d{1,2}) *([A-Za-z0-9\-]*) *([0-9\.]*) *([A-Za-z0-9\-_]*) *(\w*)$'
        switches = re.findall(verregex, showver, re.MULTILINE)

        for member in switches:
            if version not in member:
                return (False, member[3], member[5])

        return (True, member[3], member[5])

    def _upgrade_to_install(self, uri):
        self._checksession() 
        logging.info("Check file exists")

        flashuri = self.session._gen_full_path(uri.split("/")[-1])
        if not self.session._check_file_exists(flashuri):
            self.copy_file(uri)

        self.save_config()

        logging.info("Upgrading IOS XE Lite to INSTALL mode")
        command = "install add file {} activate commit auto-copy\n".format(
            flashuri)
        self.session.device.timeout = 1800
        self.session.device.write_channel(command)
        output = self.session.device.read_until_prompt_or_pattern(
            "This operation requires a reload of the system. Do you want to proceed?")
        self.session.device.write_channel("y\n")

        # This reboots the device so we have no need to call self.reload_device()
        # Unfortunately the session won't die on its own as we are connected to a
        # Serial terminal so we should kill it ourselves

        self.tserver.reset()
        return True