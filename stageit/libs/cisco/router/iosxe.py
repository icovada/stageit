from stageit.libs.BaseDevice import BaseDevice
import re
import logging


class IOSXERouter(BaseDevice):
    def upgrade_software(self, version, uri, mode="INSTALL"):
        self.status = "Checking firmware versions"
        logging.info(self.status)
        firmware = (False, None, None)
        try:
            version = re.findall(
                r'isr4300-universalk9(?:_npe)*\.(\d*\w*\.\d*\w*\.\d*\w*)\.', uri)[0]
        except IndexError:
            raise Warning("Unsupported image file")

        if not self._check_rommon():
            with self.driver(**self.sessiondata) as session:
                self.copy_file(session,
                               "http://10.82.135.9/ios-xe/isr4200_4300_rommon_169_1r_SPA.pkg")
                self.status = "Upgrading ROMMON"
                logging.info(self.status)
                driver.device.timeout = 600  # Takes at least a good 5 min
                driver.device.write_channel(
                    "upgrade rom-monitor filename bootflash:isr4200_4300_rommon_169_1r_SPA.pkg all\n")
                driver.device.read_until_prompt_or_pattern(
                    "ROMMON upgrade complete")

            self.reload_device()

        while not firmware[0]:
            firmware = self._firmware_ok(version, mode)
            if not firmware[0]:  # If firmware is not ok
                if not self._has_connectivity:
                    raise ConnectionError("Cannot copy file, device has no IP")
                # Check if firmware is version 03
                # Version 03 cannot expand version 16 directly and need to be booted in BUNDLE mode first

                oldmajor = int(firmware[1].split(".")[0])
                newmajor = int(version.split(".")[0])

                if oldmajor < 16:
                    if newmajor > 15:
                        upgradestatus = self.upgrade_to_bundle(uri)

                if mode == "BUNDLE":
                    upgradestatus = self._upgrade_to_bundle(uri)
                else:
                    upgradestatus = self._upgrade_to_install(uri)

            else:
                upgradestatus = True

            return upgradestatus

    def _firmware_ok(self, version, mode='INSTALL'):
        with self.driver(**self.sessiondata) as session:
            self.status = "Checking IOS XE version"
            logging.info(self.status)
            showver = session.device.send_command("show version")

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
        with self.driver(**self.sessiondata) as session:
            self.status = "Checking ROMMON version"
            logging.info(self.status)
            command = "show rom-monitor RP active\n"
            showrommon = session.device.send_command(command)

            # This regex parses this output:
            # System Bootstrap, Version 16.7(3r), RELEASE SOFTWARE

            romregex = r'Version (\d*\.\d)'
            currommon = re.findall(romregex, showrommon, re.MULTILINE)[0]

            return float(currommon) > 16

    def _upgrade_to_install(self, uri):
        with self.driver(**self.sessiondata) as session:
            self.status = "Check file exists"
            logging.info(self.status)

            flashuri = session._gen_full_path(uri.split("/")[-1])
            if not session._check_file_exists(flashuri):
                self.copy_file(session, uri)

            self.status = "Upgrading IOS-XE to INSTALL mode"
            logging.info(self.status)
            command = "request platform software package expand file {}\n".format(
                flashuri)
            session.device.timeout = 1800
            session.device.write_channel(command)
            output = session.device.read_until_prompt_or_pattern(
                "SUCCESS: Finished expanding")

            if "FAILED:" in output:
                return False
            else:
                if "different version of provisioning file packages.conf already exists" in output:
                    confregex = r'WARNING: (\w*\:.*)'
                    bootvaruri = re.findall(confregex, output)[0]
                else:
                    bootvaruri = "bootflash:packages.conf"

                confset = ["no boot system",
                           "boot system {}".format(bootvaruri)]
                session.device.send_config_set(confset)
                session.device.send_command("wr\n\n\n\n\n\n\n\n")

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
            session.device.send_command("wr\n\n\n\n\n\n\n\n")
        self.reload_device()
        return True
