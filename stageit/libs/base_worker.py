"""Base Worker thread from which BaseDevice is spawned."""

from threading import Thread
from time import sleep
import logging
from uuid import uuid4
import pickle
from datetime import datetime
from stageit.libs.fakeio import FakeIO
from stageitweb.stageit.models import History, Tasks
from stageit.celery import app
from jinja2 import Environment, BaseLoader
from stageit.libs.base_device import BaseDevice


class BaseWorker(Thread):
    """Base class to connect to network device."""

    name = "stageit.libs.base_worker"

    def __init__(self, cservermgmt, **kwargs):
        """Init worker thread."""
        self.hostname = None
        self.port = None
        self.transport = None
        # TODO: Pass these from template
        self.username = None
        self.password = None
        self.line = None
        self.pkid = kwargs.get('fktask')

        self.status = "Initializing"
        self.history = History()
        self.history.pkid = uuid4()
        self.history.save()

        self.logbuffer = FakeIO(self.history.pkid)

        self.task = Tasks.objects.get(pkid=self.pkid)
        self.template = self.task.fktemplate

        self.cservermgmt = cservermgmt

    def run(self, **kwargs):
        """Multithreading calls this to start the task."""
        logging.info("Worker for %s:%s ready", self.hostname, self.port)

        self.hostname = kwargs.get('hostname')
        self.port = kwargs.get('port')
        self.transport = kwargs.get('transport')
        # TODO: Pass these from template
        self.username = kwargs.get('username', 'cisco')
        self.password = kwargs.get('password', 'cisco')
        self.line = kwargs.get('line')
        self.status = "Initializing"

        rtemplate = Environment(
            loader=BaseLoader).from_string(self.template.template)

        self.description = self.task.description
        self.templatevalues = pickle.loads(self.task.taskvalues)
        self.template = self.template.template
        self.finalconfig = rtemplate.render(
            **pickle.loads(self.task.taskvalues))
        self.platform = self.template.platform
        self.poststaging = self.template.poststaging
        self.filepath = self.template.filepath
        self.installmode = self.template.installmode

        self.history.datestart=datetime.utcnow(),
        self.history.description=self.description,
        self.history.installmode=self.installmode,
        self.history.templatevalues=self.task.taskvalues,
        self.history.template=self.template
        self.history.save()

        # Data to pass to Worker class
        self.devicedata = {'hostname': self.hostname,
                           'port': self.port,
                           'transport': self.transport,
                           'username': self.username,
                           'password': self.password,
                           'platform': self.platform,
                           'logbuffer': self.logbuffer,
                           'history': self.history}

        self.tempconfig = {"username": "cisco",
                            "password": "cisco"}

        self.status = "Discovering platform"
        self.driver = self.find_model()

        self.status = "Working"
        # Actually do the job (finally!)
        self.stageit()

        self.history.rundata = pickle.dumps({'Run Log': self.driver.getlog()})

        self.task.delete()
        self.history.dateend = datetime.utcnow()
        self.history.save()


    def find_model(self):
        """Find device type and return appropriate class to deal with
        upgrading, version checking and else."""
        device = BaseDevice(**self.devicedata,
                            cservermgmt=self.cservermgmt)

        device.checkavailable(300)

        if any(model in device.facts["model"] for model in
               ("C3650", "C3850")):
            device.close()
            from stageit.libs.cisco.switch.iosxe import IOSXESwitch
            specific_device = IOSXESwitch(
                **self.devicedata, cservermgmt=self.cservermgmt)
        elif any(model in device.facts["model"] for model in
                 ("4221", "4321", "4331", "4351", "4431", "4451", "4461")):
            device.close()
            from stageit.libs.cisco.router.iosxe import IOSXERouter
            specific_device = IOSXERouter(
                **self.devicedata, cservermgmt=self.cservermgmt)
        elif any(model in device.facts["model"] for model in ("2960", "3560CX")):
            device.close()
            from stageit.libs.cisco.switch.ios import IOSSwitch
            specific_device = IOSSwitch(
                **self.devicedata, cservermgmt=self.cservermgmt)

        else:
            raise ValueError("Unrecognised model")

        return specific_device

    def getstatus(self):
        """Return status of Worker or Device."""
        if self.status == 'Working':
            return self.driver.status
        else:
            return self.status

    def stageit(self):
        """Do the job."""
        self.status = 'Working'
        self.driver.checkavailable(1000)

        # Skip upgrade if file path not provided
        if self.filepath != '':
            try:
                self.driver.upgrade_software(uri=self.filepath,
                                             mode=self.installmode)
            except ConnectionError:
                self.driver.load_temp_config(**self.tempconfig)
                sleep(3)
                self.driver.upgrade_software(uri=self.filepath,
                                             mode=self.installmode)

        self.driver.load_final_config(self.template, **self.templatevalues)


@app.task()
def baseworker(**kwargs):
    worker = BaseWorker(**kwargs)
    return worker.run(**kwargs)
