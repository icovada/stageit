"""Use with IOS-XE routers such as ISR 4000."""
import re
import logging
from libs.base_device import BaseDevice


class IOSXERouter(BaseDevice):
    """Expand BaseDevice with ISR4000-specific commands."""

    def upgrade_software(self, uri, mode="INSTALL"):
        """Verify software version and if necessary upgrade through proper path."""
        logging.info("Checking firmware versions")
        firmware = (False, None, None)
        if re.search(r'isr4300-universalk9(_npe)?(\.(\d{2})){3}\.SPA\.bin', uri):
            # ISR 4000
            # isr4300-universalk9.16.09.03.SPA.bin
            # isr4300-universalk9_npe.16.09.03.SPA.bin
            version = re.findall(
                r'isr4300-universalk9(_npe)?(\.(\d{2})){3}\.SPA\.bin', uri)[0]

        if re.search(r'cat9k_iosxe(ldpe)?(\.(\d{2})){3}\.SPA\.bin', uri):
            # Catalyst 9500, 9600
            # cat9k_iosxe.16.09.03.SPA.bin
            # cat9k_iosxeldpe.16.09.03.SPA.bin
            version = re.findall(
                r'cat9k_iosxe(ldpe)?(\.(\d{2})){3}\.SPA\.bin', uri)[0]
        else:
            self.session.close()
            raise Warning("Unsupported image file")

        if not self._check_rommon():
            self._checksession()
            self.copy_file(
                "http://10.82.135.9/ios-xe/isr4200_4300_rommon_169_1r_SPA.pkg")
            logging.info("Upgrading ROMMON")
            self.session.device.timeout = 600  # Takes at least a good 5 min
            self.session.device.write_channel(
                "upgrade rom-monitor filename bootflash:isr4200_4300_rommon_169_1r_SPA.pkg all\n")
            self.session.device.read_until_prompt_or_pattern(
                "ROMMON upgrade complete")

            self.reload_device()

        while not firmware[0]:
            firmware = self._firmware_ok(version, mode)
            if not firmware[0]:  # If firmware != ok
                if not self._has_connectivity:
                    raise ConnectionError("Cannot copy file, device has no IP")
                # Check if firmware is version 03
                # Version 03 cannot expand version 16 directly
                # and need to be booted in BUNDLE mode first

                oldmajor = int(firmware[1].split(".")[0])
                newmajor = int(version.split(".")[0])

                if oldmajor < 16 and newmajor > 15:
                    upgradestatus = self._upgrade_to_bundle(uri)

                if mode == "BUNDLE":
                    upgradestatus = self._upgrade_to_bundle(uri)
                else:
                    upgradestatus = self._upgrade_to_install(uri)

            else:
                upgradestatus = True

            return upgradestatus

    def _firmware_ok(self, version, mode='INSTALL'):
        self._checksession()
        logging.info("Checking IOS XE version")
        showver = self.session.device.send_command("show version")

        # This regex parses the following output
        # System image file is "bootflash:/isr4300-universalk9.03.13.04.S.154-3.S4-ext.SPA.bin"
        # System image file is "packages.conf"
        moderegex = r'image file is .*\.(\w*)'
        curmode = re.findall(moderegex, showver, re.MULTILINE)
        modemapping = {'bin': 'BUNDLE',
                       'conf': 'INSTALL'}

        installmode = modemapping[curmode[0]]

        # This regex parses the following output
        # Cisco IOS XE Software, Version 03.13.04.S - $(release_mode)
        # Cisco IOS XE Software, Version 03.13.04a.S - $(release_mode)

        verregex = r'IOS XE Software, Version (\d\d\.\d\d\.\d\d\w*)'
        curversion = re.findall(verregex, showver, re.MULTILINE)[0]

        verok = True if version == curversion else False
        modeok = True if installmode == mode else False

        if verok and modeok:
            return (True, curversion, installmode)
        else:
            return (False, version, installmode)

    def _check_rommon(self):
        self._checksession()
        logging.info("Checking ROMMON version")
        command = "show rom-monitor RP active\n"
        showrommon = self.session.device.send_command(command)

        # This regex parses this output:
        # System Bootstrap, Version 16.7(3r), RELEASE SOFTWARE

        romregex = r'Version (\d*\.\d)'
        currommon = re.findall(romregex, showrommon, re.MULTILINE)[0]

        return float(currommon) > 16

    def _upgrade_to_install(self, uri):
        self._checksession()
        logging.info("Check file exists")

        flashuri = self.session._gen_full_path(uri.split("/")[-1])
        if not self.session._check_file_exists(flashuri):
            self.copy_file(uri)

        logging.info("Upgrading IOS-XE to INSTALL mode")
        command = "request platform software package expand file {}\n".format(
            flashuri)
        self.session.device.timeout = 1800
        self.session.device.write_channel(command)
        output = self.session.device.read_until_prompt_or_pattern(
            "SUCCESS: Finished expanding")

        if "FAILED:" in output:
            return False
        else:
            if "different version of provisioning file packages.conf already exists" in output:
                # TODO: Add output of command in comments
                confregex = r'WARNING: (\w*\:.*)'
                bootvaruri = re.findall(confregex, output)[0]
            else:
                bootvaruri = "bootflash:packages.conf"

            confset = ["no boot system",
                       "boot system {}".format(bootvaruri)]
            self.session.device.send_config_set(confset)
            self.session.device.send_command("wr\n\n\n\n\n\n\n\n")

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
        self.session.device.send_command("wr\n\n\n\n\n\n\n\n")
        self.reload_device()
        return True
