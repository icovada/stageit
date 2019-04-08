import threading
import queue
from stageit.BaseDevice import BaseDevice


class BaseWorker():
    """
    Base class to connect to network device
    """

    def __init__(self, hostname, port, transport, vendor, username, password):
        self.q = q
        self.hostname = hostname
        self.port = port
        self.transport = transport
        self.vendor = vendor
        self.username = username
        self.password = password

        self.status = "Initializing"

        self.driver = self.find_model()
        self.status = "Model found"

    def find_model(self):
        """
        Find device type and return appropriate class to deal with upgrading,
        version checking and else
        """

        device = BaseDevice(self.hostname,
                            self.port,
                            self.transport,
                            self.vendor,
                            self.username,
                            self.password, retries=60)

        self.status = "Connected to " + device.facts["model"]
        if "C3650" in device.facts["model"]:
            from stageit.cisco.switch.iosxe import IOSXESwitch
            specific_device = IOSXESwitch(self.hostname,
                                          self.port,
                                          self.transport,
                                          self.vendor,
                                          self.username,
                                          self.password)

        else:
            raise ValueError("Unrecognised model")

        return specific_device
