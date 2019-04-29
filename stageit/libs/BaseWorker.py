from threading import Thread
import queue
from stageit.libs.BaseDevice import BaseDevice
from stageit.libs.db import Templates, History, Tasks, newsession
from time import sleep
import logging
from uuid import uuid4
import pickle
from jinja2 import Environment, BaseLoader
from datetime import datetime



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
        # TODO: Pass these from template
        self.username = "cisco"
        self.password = "cisco"

        self.status = "Initializing"

    def run(self):
        logging.info("Worker for {}:{} ready".format(self.hostname, self.port))
        while True:
            try:
                self.status = "Waiting for work"
                taskid = self.q.get(timeout=600)

            except queue.Empty:
                self.status = "Dead"
                return

            session = newsession()

            task = session.query(Tasks).get(taskid)
            template = task.template
            rtemplate = Environment(
                loader=BaseLoader).from_string(template.template)

            self.description = task.description
            self.templatevalues = pickle.loads(task.taskvalues)
            self.template = template.template
            self.finalconfig = rtemplate.render(
                **pickle.loads(task.taskvalues))
            self.platform = template.platform
            self.poststaging = template.poststaging
            self.filepath = template.filepath

            self.pkid = str(uuid4())

            self.dbrow = History(
                pkid=self.pkid,
                datestart=datetime.utcnow(),
                description=self.description,
                templatevalues=task.taskvalues,
                template=self.template
            )

            self.devicedata = {'hostname': self.hostname,
                               'port': self.port,
                               'transport': self.transport,
                               'username': self.username,
                               'password': self.password,
                               'platform': self.platform,
                               'pkid': self.pkid}


            self.tempconfig = {"username": "cisco",
                               "password": "cisco"}
            session.add(self.dbrow)
            session.commit()

            self.status = "Discovering platform"
            self.driver = self.find_model()

            self.status = "Working"
            self.stageit()

            session.rundata=pickle.dumps({'Run Log': self.driver.getlog()})

            session.delete(task)
            self.dbrow.dateend=datetime.utcnow()
            session.commit()
            self.q.task_done()

    def find_model(self):
        """
        Find device type and return appropriate class to deal with upgrading,
        version checking and else
        """

        device = BaseDevice(**self.devicedata)

        device.checkavailable(300)

        if any(model in device.facts["model"] for model in ("C3650", "C3850")):
            device.close()
            from stageit.libs.cisco.switch.iosxe import IOSXESwitch
            specific_device = IOSXESwitch(**self.devicedata)
        elif any(model in device.facts["model"] for model in ("4221", "4321", "4331", "4351", "4431", "4451", "4461")):
            device.close()
            from stageit.libs.cisco.router.iosxe import IOSXERouter
            specific_device = IOSXERouter(**self.devicedata)
        elif any(model in device.facts["model"] for model in ("2960", "3560CX")):
            device.close()
            from stageit.libs.cisco.switch.ios import IOSSwitch
            specific_device = IOSXERouter(**self.devicedata)

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

        # Skip upgrade if file path not provided
        if self.filepath != '':
            try:
                self.driver.upgrade_software(uri=self.filepath)
                                             # TODO mode=self.work['mode'])
            except ConnectionError:
                self.driver.load_temp_config(**self.tempconfig)
                sleep(3)
                self.driver.upgrade_software(uri=self.filepath)
                                             # TODO mode=self.work['mode'])

        self.driver.load_final_config(self.template, **self.templatevalues)
                
                
