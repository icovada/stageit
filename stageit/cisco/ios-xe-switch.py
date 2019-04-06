from stageit.BaseDevice import BaseDevice

class IOSXESwitch(BaseDevice):
    def upgrade_switch(self):
        # regex to find switch stack ^\*? *(\d) (\d{1,2}) *([A-Z\-0-9])* *([A-Z\-0-9.])* *([A-Za-z\-_0-9.])* ([A-Z])*
        pass