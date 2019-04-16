from threading import Thread
import queue
from time import sleep
from io import BytesIO


class FakeWorker(Thread):
    """
    Fake for test
    """

    def __init__(self, q, hostname, port, transport, **kwargs):
        Thread.__init__(self)
        self.q = q
        self.hostname = hostname
        self.port = port
        self.transport = transport
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

            self.status = "Discovering model"
            driver = self.find_model()

            self.q.task_done()

    def find_model(self):
        """
        Return dummy data
        """
        self.status = ("{} Status 1/5".format(self.work))
        self.log.write(b'1')
        sleep(5)
        self.status = ("{} Status 2/5".format(self.work))
        self.log.write(b'2')
        sleep(5)
        self.status = ("{} Status 3/5".format(self.work))
        self.log.write(b'3')
        sleep(5)
        self.status = ("{} Status 4/5".format(self.work))
        self.log.write(b'4')
        sleep(5)
        self.status = ("{} Status 5/5".format(self.work))
        self.log.write(b'5')
        sleep(5)

        return True

    def getlog(self):
        return self.log.getvalue()