import stageit.BaseDevice
import re

class IOSXESwitch(stageit.BaseDevice.BaseDevice):
    def upgrade_switch(self):
        raise NotImplementedError

class C3650(IOSXESwitch):
    def firmware_ok(self, firmware):
        with self.driver(**self.sessiondata) as session:
            showver = session.device.send_command("show ver")

            # This regex parses the following output
            # Taken from https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst3650/software/release/3se/system_management/configuration_guide/b_sm_3se_3650_cg/b_sm_3se_3650_cg_chapter_010101.html

            # Package: Base, version: 03.02.00SE, status: active
            # File: cat3k_caa-base.SPA.03.02.00SE.pkg, on: Switch1
            # Built: Wed Jan 09 21:59:52 PST 2013, by: gereddy

            # Package: Drivers, version: 03.02.00.SE, status: active
            # File: cat3k_caa-drivers.SPA.03.02.00.SE.pkg, on: Switch1
            # Built: Wed Jan 09 22:03:41 PST 2013, by: gereddy

            # Package: Infra, version: 03.02.00SE, status: active
            # File: cat3k_caa-infra.SPA.03.02.00SE.pkg, on: Switch1
            # Built: Wed Jan 09 22:00:56 PST 2013, by: gereddy

            # Package: IOS, version: 150-1.EX, status: active
            # File: cat3k_caa-iosd-universalk9.SPA.150-1.EX.pkg, on: Switch1
            # Built: Wed Jan 09 22:02:23 PST 2013, by: gereddy

            # Package: Platform, version: 03.02.00.SE, status: active
            # File: cat3k_caa-platform.SPA.03.02.00.SE.pkg, on: Switch1
            # Built: Wed Jan 09 22:01:46 PST 2013, by: gereddy

            # Package: WCM, version: 10.0.100.0, status: active
            # File: cat3k_caa-wcm.SPA.10.0.100.0.pkg, on: Switch1
            # Built: Wed Jan 09 22:03:05 PST 2013, by: gereddy

            verregex = r'cat3k_caa-([a-z0-9\-]*)\.(.*)\.pkg, on: (.*)'
            switches = re.findall(verregex,showver,re.MULTILINE)

            verdict = {}
            for i in switches:
                verdict[i[2]] = {}
            
            for i in switches:
                verdict[i[2]][i[0]] = i[1]

            for member in switches:
                if firmware not in member['base']:
                    return False
            
            return True
            