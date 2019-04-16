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
        for i in range(60):
            text = "{} Status {}/60\n".format(self.work, i)
            self.status = (text)
            self.log.write(text.encode('utf-8'))
            sleep(0.5)

        return True

    def getlog(self):
        return self.log.getvalue().decode('utf-8')