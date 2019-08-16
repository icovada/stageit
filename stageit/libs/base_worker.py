"""Base Worker thread from which BaseDevice is spawned."""

from time import sleep
import logging
from uuid import uuid4
import pickle
from datetime import datetime
from stageit.libs.fakeio import FakeIO
from stageit.celery import app
from celery import Task
from jinja2 import Environment, BaseLoader
from stageit.libs.base_device import BaseDevice
import requests

URL_BASE = "http://localhost:8000/api/"
URL_SUFFIX = "/?format=json"


class BaseWorker(Task):
    """Base class to connect to network device."""

    name = "stageit.libs.base_worker.baseworker"

    def run(self, *args, **kwargs):
        """Celery calls this to start the task."""

        self.pkid = kwargs.get('fkhistory')
        self.logbuffer = FakeIO(self.pkid)
        logging.info('Worker for {} ready'.format(self.pkid))

        # Get History row from DB. From here, discover everything else
        self.historydata = requests.get(
            URL_BASE + 'history/' + self.pkid + URL_SUFFIX).json()

        if self.historydata.get('workerid') is not None:
            raise AssertionError(
                "Task already being worked on by someone else")
        else:
            # Mark History row as being worked on by us
            data = {'workerid': kwargs.get('celeryid'),
                    'status': 'In progress'}
            requests.put(URL_BASE + 'history/' +
                         self.pkid + URL_SUFFIX, data=data)

        # Now we have checked the task is OK to work on and marked it as ours, fetch task data
        fktask = self.historydata.get('fktask')
        self.taskdata = requests.get(
            URL_BASE + 'task/' + fktask + URL_SUFFIX).json()

        # From the task we find the template
        fktemplate = self.taskdata.get('fktemplate')
        self.templatedata = requests.get(
            URL_BASE + 'template/' + fktemplate + URL_SUFFIX).json()

        # Find the port to connect to
        self.serialportdata = requests.get(
            URL_BASE + 'serialport/' + self.historydata.get('fkserialport') + URL_SUFFIX).json()

        # Find the terminal server to connect to
        self.terminalserverdata = requests.get(
            URL_BASE + 'terminalserver/' + self.serialportdata.get('fkterminalserver') + URL_SUFFIX).json()
        logging.info('Successfully retrieved all data')

        hostname = self.terminalserverdata.get('hostname')
        port = self.serialportdata.get('port')
        transport = self.serialportdata.get('port')

        # TODO: Pass these from template
        username = 'cisco'
        password = 'cisco'

        description = self.taskdata.get('description')
        taskvalues = self.taskdata.get('taskvalues')
        self.template = self.templatedata.get('template')
        rtemplate = Environment(loader=BaseLoader).from_string(template)
        self.finalconfig = rtemplate.render(taskvalues)
        platform = self.templatedata.get('platform')
        poststaging = self.templatedata.get('poststaging')
        self.filepath = self.templatedata.get('filepath')
        self.installmode = self.templatedata.get('installmode')

        data = {'datestart': datetime.utcnow(),
                'description': description,
                'installmode': self.installmode,
                'templatevalues': taskvalues,
                'template': self.template}

        # Data to pass to Worker class
        self.devicedata = {'hostname': hostname,
                           'port': port,
                           'transport': transport,
                           'username': username,
                           'password': password,
                           'platform': platform,
                           'logbuffer': self.logbuffer
                           }

        self.tempconfig = {"username": "cisco",
                           "password": "cisco"}

        # Find driver for Terminal Server
        if self.terminalserverdata.get('model') == 'cisco':
            from stageit.libs.consoleserver.cisco import CiscoConsoleServer as tserver
        else:
            from stageit.libs.consoleserver import BaseConsoleServer as tserver

        # Instantiate terminal server class
        self.tserver = tserver(
            {**self.serialportdata, **self.terminalserverdata})

        logging.info('Discovering platform')
        self.driver = self.find_model()

        self.status = "Working"
        # Actually do the job (finally!)
        self.stageit()

        requests.delete(URL_BASE + 'templates/' + fktask + URL_SUFFIX)
        data = {'status': 'Completed',
                'dateend': datetime.utcnow()
                }
        requests.put(URL_BASE + 'history/' + self.pkid + URL_SUFFIX, data=data)


    def find_model(self):
        """Find device type and return appropriate class to deal with
        upgrading, version checking and else."""
        device = BaseDevice(**self.devicedata,
                            tserver=self.tserver)
        device.checkavailable(300)

        if any(model in device.facts["model"] for model in
               ("C3650", "C3850")):
            device.close()
            from stageit.libs.cisco.switch.iosxe import IOSXESwitch
            specific_device = IOSXESwitch(
                **self.devicedata, tserver=tserver)
        elif any(model in device.facts["model"] for model in
                 ("4221", "4321", "4331", "4351", "4431", "4451", "4461")):
            device.close()
            from stageit.libs.cisco.router.iosxe import IOSXERouter
            specific_device = IOSXERouter(
                **self.devicedata, tserver=tserver)
        elif any(model in device.facts["model"] for model in ("2960", "3560CX")):
            device.close()
            from stageit.libs.cisco.switch.ios import IOSSwitch
            specific_device = IOSSwitch(
                **self.devicedata, tserver=tserver)

        else:
            raise ValueError("Unrecognised model")

        return specific_device

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

        self.driver.load_final_config(self.finalconfig)


app.register_task(BaseWorker())


@app.task(bind=True, base=BaseWorker)
def baseworker(self, **kwargs):
    celeryid = self.request.id.__str__()
    worker = BaseWorker()
    return worker.run(fkhistory=kwargs.get('fkhistory'), celeryid=celeryid)
