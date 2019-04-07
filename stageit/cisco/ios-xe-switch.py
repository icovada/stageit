from stageit.BaseDevice import BaseDevice


class IOSXESwitch(BaseDevice):
    def firmware_ok(self, firmware):
        with self.driver(**self.sessiondata) as session:
            showver = session.device.send_command("show ver")

            # This regex parses the following output:

            verregex = r"^\*? *(\d) (\d{1,2}) *([A-Z\-0-9]*) *([A-Z\-0-9.]*) *([A-Za-z\-_0-9.]*) ([A-Z])*"
            switches = re.self


    def upgrade_switch(self):
        import re
        # regex to find switch stack 
        