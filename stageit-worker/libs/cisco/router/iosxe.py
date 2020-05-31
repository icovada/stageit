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
        logging.debug('About to detect version from file name')
        if re.search(r'isr4300-universalk9(_npe)?(\.(\d{2})){3}\.SPA\.bin', uri):
            # ISR 4000
            # isr4300-universalk9.16.09.03.SPA.bin
            # isr4300-universalk9_npe.16.09.03.SPA.bin
            version = re.findall(
                r'isr4300-universalk9(_npe)?(\.(\d{2})){3}\.SPA\.bin', uri)[0]
            logging.debug('Detected version: %s', version)
        else:
            logging.debug('Version not found, unsupported image file')
            self.session.close()
            logging.error('Unsupported image file %s', uri)
            raise Warning(f'Unsupported image file {uri}')

        while not firmware[0]:
            firmware = self._firmware_ok(version, mode)
            if not firmware[0]:  # If firmware != ok
                logging.info("Firmware needs to be upgraded")
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

        logging.debug('File type is %s', curmode[0])
        installmode = modemapping[curmode[0]]
        logging.debug('Install mode: %s', installmode)

        # This regex parses the following output
        # Cisco IOS XE Software, Version 03.13.04.S - $(release_mode)
        # Cisco IOS XE Software, Version 03.13.04a.S - $(release_mode)

        verregex = r'IOS XE Software, Version (\d\d\.\d\d\.\d\d\w*)'
        curversion = re.findall(verregex, showver, re.MULTILINE)[0]

        logging.debug('Current version is %s', curversion)

        verok = True if version == curversion else False
        logging.debug('Version check %s', verok)
        modeok = True if installmode == mode else False
        logging.debug('Mode check %s', modeok)

        if verok and modeok:
            return (True, curversion, installmode)
        else:
            return (False, version, installmode)

    def _upgrade_to_install(self, uri):
        self._checksession()
        logging.info("Check file exists")

        flashuri = self.session._gen_full_path(uri.split("/")[-1])
        if not self.session._check_file_exists(flashuri):
            logging.info('File does not exist on flash, start copy')
            self.copy_file(uri)

        logging.info("Upgrading IOS-XE to INSTALL mode")
        command = "request platform software package expand file {}\n".format(
            flashuri)
        self.session.device.timeout = 1800
        logging.debug('send command %s', command)
        self.session.device.write_channel(command)
        output = self.session.device.read_until_prompt_or_pattern(
            "SUCCESS: Finished expanding")

        if "FAILED:" in output:
            logging.error('Upgrade failed')
            return False
        else:
            if "different version of provisioning file packages.conf already exists" in output:
                # TODO: Add output of command in comments
                confregex = r'WARNING: (\w*\:.*)'
                bootvaruri = re.findall(confregex, output)[0]
            else:
                bootvaruri = "bootflash:packages.conf"

            logging.info('bootvaruri: %s', bootvaruri)

            confset = ["no boot system",
                       "boot system {}".format(bootvaruri)]
            logging.info('Setting bootvar and reloading')
            self.session.device.send_config_set(confset)
            self.session.device.send_command("wr\n\n\n\n\n\n\n\n")

        self.reload_device()
        return True

    def _upgrade_to_bundle(self, uri):
        self._checksession()
        logging.info("Check file exists")

        flashuri = self.session._gen_full_path(uri.split("/")[-1])
        logging.debug('Checking if %s exists', flashuri)
        if not self.session._check_file_exists(flashuri):
            logging.debug('File does not exist, starting copy')
            self.copy_file(uri)
        else:
            logging.debug('File exists, proceeding')

        logging.info("Upgrading IOS-XE to BUNDLE mode")
        confset = ["no boot system", "boot system {}".format(flashuri)]
        self.session.device.send_config_set(confset)
        logging.info('Setting bootvar and reloading')
        self.session.device.send_command("wr\n\n\n\n\n\n\n\n")
        self.reload_device()
        return True
