from threading import Thread
import queue
from stageit.libs.BaseDevice import BaseDevice
from io import BytesIO


class BaseWorker(Thread):
    """
    Base class to connect to network device
    """

    def __init__(self, q, **kwargs):
        Thread.__init__(self)
        self.q = q
        self.hostname = kwargs['hostname']
        self.port = kwargs['port']
        self.transport = kwargs['transport']

        self.status = "Initializing"

    def run(self):
        while True:
            try:
                self.log = BytesIO()
                self.status = "Waiting for work"
                self.work = self.q.get(timeout=60)

            except queue.Empty:
                self.status = "Dead"
                return

            self.work['hostname'] = self.hostname
            self.work['port'] = self.port
            self.work['transport'] = self.transport
            self.status = "Discovering platform"
            self.driver = self.find_model()
            self.status = "Working"
            self.stageit()
            self.q.task_done()

    def find_model(self):
        """
        Find device type and return appropriate class to deal with upgrading,
        version checking and else
        """

        device = BaseDevice(**self.work)

        device.checkavailable(300)

        if "C3650" in device.facts["model"]:
            device.close()
            from stageit.libs.cisco.switch.iosxe import IOSXESwitch
            specific_device = IOSXESwitch(**self.work)
        if "4331" in device.facts['model']:
            device.close()
            from stageit.libs.cisco.router.iosxe import IOSXERouter
            specific_device = IOSXERouter(**self.work)

        else:
            raise ValueError("Unrecognised model")

        return specific_device

    def getstatus(self):
        if self.status == 'Working':
            return self.driver.status
        else:
            return self.status

    def stageit(self):
        self.status = 'Working'
        self.driver.checkavailable(1000)
        self.driver.getfacts()
        try: 
            self.driver.upgrade_software(version=self.work['version'],
                                         uri=self.work['uri'],
                                         mode=self.work['mode'])
        except ConnectionError:
            self.driver.load_temp_config(**self.work['tempconfig'])
            self.driver.upgrade_software(version=self.work['version'],
                                         uri=self.work['uri'],
                                         mode=self.work['mode'])
        
        self.driver.load_final_config(**self.work['finalconfig'])