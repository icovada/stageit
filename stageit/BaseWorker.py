import threading
import queue
from stageit.BaseDevice import BaseDevice


class BaseWorker(threading.Thread):

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
                self.status = "Discovering model"
                driver = self.find_model(**self.work)

            except queue.Empty():
                return

        self.q.task_done()

    def find_model(self, **kwargs):
        device = BaseDevice(**kwargs)
        self.status = "Connecting to " + device.facts["model"]
        if "C3650" in device.facts["model"]:
            from stageit.cisco.switch.iosxe import IOSXESwitch
            specific_device = IOSXESwitch(**kwargs)

        else:
            raise ValueError("Unrecognised model")

        return specific_device