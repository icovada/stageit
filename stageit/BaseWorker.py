import threading
import queue
from stageit.BaseDevice import BaseDevice


class BaseWorker(threading.Thread):
    """
    Base class to connect to network device
    """

    def __init__(self, q, hostname, port, transport):
        self.q = q
        self.hostname = hostname
        self.port = port
        self.transport = transport
        self.status = "Initializing"

    def run(self):
        while True:
            try:
                self.work = self.q.get(timeout=60)

            except queue.Empty():
                return

        self.status = "Discovering model"
        driver = self.find_model(**self.work)

        
        self.q.task_done()

    def find_model(self, **kwargs):
        """
        Find device type and return appropriate class to deal with upgrading,
        version checking and else
        """

        device = BaseDevice(**kwargs)
        self.status = "Connecting to " + device.facts["model"]
        if "C3650" in device.facts["model"]:
            from stageit.cisco.switch.iosxe import C3650
            specific_device = C3650(**kwargs)

        else:
            raise ValueError("Unrecognised model")

        return specific_device