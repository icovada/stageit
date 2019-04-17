from stageit.libs.BaseDevice import BaseDevice
import re


class IOSXERouter(BaseDevice):
    def upgrade_software(self, version, uri, mode="INSTALL"):
        self.status = "Checking firmware versions"
        if not self._check_rommon():
            self.copy_file(
                "http://10.82.135.9/ios-xe/isr4200_4300_rommon_169_1r_SPA.pkg")
            self.reload()

        firmware = (False, None, None)
        while not firmware[0]:
            firmware = self._firmware_ok(version, mode)
            if not firmware[0]:  #If firmware is not ok
                if self._has_connectivity is False:
                    raise ConnectionError("Cannot copy file, device has no IP")
                # Check if firmware is version 03
                # Version 03 cannot expand version 16 directly and need to be booted in BUNDLE mode first

                oldmajor = int(firmware[1].split(".")[0])
                newmajor = int(version.split(".")[0])

                self.load_temp_config()

                if oldmajor < 16:
                    if newmajor > 15:
                        upgradestatus = self.upgrade_to_bundle(uri)

                if mode == "BUNDLE":
                    upgradestatus = self._upgrade_to_bundle(uri)
                else:
                    upgradestatus = self._upgrade_to_install(uri)

            return upgradestatus

    def _firmware_ok(self, version, mode='INSTALL'):
        with self.driver(**self.sessiondata) as session:
            self.status = "Checking IOS XE version"
            showver = session.device.send_command("show version")

            # This regex parses the following output
            # System image file is "bootflash:/isr4300-universalk9.03.13.04.S.154-3.S4-ext.SPA.bin"
            # System image file is "packages.conf"
            moderegex = r'image file is .*\.(\w*)'
            mode = re.findall(moderegex, showver, re.MULTILINE)
            modemapping = {'bin': 'BUNDLE',
                           'conf': 'INSTALL'}

            installmode = modemapping[mode[0]]

            # This regex parses the following output
            # Cisco IOS XE Software, Version 03.13.04.S - $(release_mode)
            # Cisco IOS XE Software, Version 03.13.04a.S - $(release_mode)

            verregex = r'IOS XE Software, Version (\d\d\.\d\d\.\d\d\w*)'
            curversion = re.findall(verregex, showver, re.MULTILINE)

            verok = True if version == curversion else False
            modeok = True if installmode == mode else False

            if verok and modeok:
                return (True, curversion, installmode)
            else:
                return (False, version, installmode)

    def _check_rommon(self):
        with self.driver(**self.sessiondata) as session:
            self.status = "Checking ROMMON version"
            command = "show rom-monitor RP active\n"
            showrommon = session.device.send_command(command)

            # This regex parses this output:
            # System Bootstrap, Version 16.7(3r), RELEASE SOFTWARE

            romregex = r'Version (\d*\.\d)'
            currommon = re.findall(romregex, showrommon, re.MULTILINE)[0]

            return float(currommon) > 16

    def _upgrade_to_install(self, uri):
        with self.driver(**self.sessiondata) as session:
            self.status = "Upgrading IOS-XE to INSTALL mode"
            command = "request platform software package expand file {}\n".format(
                uri)
            session.device.timeout = 1800
            session.device.write_channel(command)
            output = session.device.read_until_prompt_or_pattern(
                "SUCCESS: Finished expanding")
            if "FAILED:" in output:
                return False
            else:
                self.reload()
                return True

    def _upgrade_to_bundle(self, uri):
        with self.driver(**self.sessiondata) as session:
            self.status = "Upgrading IOS-XE to BUNDLE mode"
            confset = ["no boot system", "boot system {}".format(uri)]
            session.device.send_config_set(confset)
            session.device.send_command("wr\n\n\n\n\n\n\n\n")
            self.reload()
            return True
