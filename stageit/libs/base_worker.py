"""Base Worker thread from which BaseDevice is spawned."""

import logging
from datetime import datetime

import requests
from celery import Task
from jinja2 import BaseLoader, Environment

from stageit.celery import app
from stageit.libs.base_device import BaseDevice
from stageit.libs.fakeio import FakeIO

URL_SUFFIX = "/?format=json"


class BaseWorker(Task):
    """Base class to connect to network device."""

    name = "stageit.libs.base_worker.baseworker"

    def on_success(self, retval, task_id, *args, **kwargs):
        """
        Celery runs this if the task runs successfully
        Update database, set history as successful and delete task.
        """
        url_base = "http://web:8000/api/"
        logging.info("Set task successful")
        logging.info(retval)
        logging.info(kwargs)

        requests.delete(url_base + 'templates/' + self.fktask + URL_SUFFIX)
        data = {'status': 'Completed',
                'dateend': datetime.utcnow()
                }
        requests.put(url_base + 'history/' + self.pkid + URL_SUFFIX, data=data)

    def on_failure(self, retval, task_id, *args, **kwargs):
        """
        Celery runs this if the task fails
        Update database, set history as failed.
        """

        url_base = "http://web:8000/api/"
        logging.error("EPIC FAIL")
        data = {'status': 'Fail',
                'dateend': datetime.utcnow()
                }
        requests.put(url_base + 'history/' + self.pkid + URL_SUFFIX, data=data)

    def run(self, *args, **kwargs):
        """Celery calls this to start the task."""

        url_base = "http://web:8000/api/"

        self.workerid = self.app.oid
        self.pkid = kwargs.get('fkhistory')
        self.logbuffer = FakeIO(self.pkid)
        logging.info('Worker for %s ready', self.pkid)

        # Get History row from DB. From here, discover everything else
        self.historydata = requests.get(
            url_base + 'history/' + self.pkid + URL_SUFFIX).json()

        if self.historydata.get('workerid') is not None:
            raise AssertionError(
                "Task already being worked on by someone else")
        else:
            # Mark History row as being worked on by us
            data = {'workerid': self.workerid,
                    'status': 'Discovering'}
            requests.put(url_base + 'history/' +
                         self.pkid + URL_SUFFIX, data=data)

        # Now we have checked the task is OK to work on and marked it as ours, fetch task data
        self.fktask = self.historydata.get('fktask')
        self.taskdata = requests.get(
            url_base + 'task/' + self.fktask + URL_SUFFIX).json()

        # From the task we find the template
        fktemplate = self.taskdata.get('fktemplate')
        self.templatedata = requests.get(
            url_base + 'template/' + fktemplate + URL_SUFFIX).json()

        # Find the port to connect to
        self.serialportdata = requests.get(
            url_base + 'serialport/' + self.historydata.get('fkserialport') + URL_SUFFIX).json()

        # Find the terminal server to connect to
        self.terminalserverdata = requests.get(
            url_base + 'terminalserver/' + self.serialportdata.get('fkterminalserver') + URL_SUFFIX).json()
        logging.info('Successfully retrieved all data')

        hostname = self.terminalserverdata.get('hostname')
        port = self.serialportdata.get('port')
        transport = self.serialportdata.get('transport')
        username = self.terminalserverdata.get('username')
        password = self.terminalserverdata.get('password')

        description = self.taskdata.get('description')
        taskvalues = self.taskdata.get('taskvalues')
        self.template = self.templatedata.get('template')
        rtemplate = Environment(loader=BaseLoader).from_string(self.template)
        self.finalconfig = rtemplate.render(taskvalues)
        platform = self.templatedata.get('platform')
        poststaging = self.templatedata.get('poststaging')
        filepath = self.templatedata.get('filepath')
        installmode = self.templatedata.get('installmode')

        data = {'datestart': datetime.utcnow(),
                'description': description,
                'installmode': installmode,
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
            **{**self.serialportdata, **self.terminalserverdata})

        logging.info('Discovering platform')
        self.driver = self.find_model(url_base)

        # Actually do the job (finally!)
        self.stageit(filepath=filepath, installmode=installmode,
                     url_base=url_base, fkbootstrapconfig=self.templatedata.get('fkbootstrapconfig'))

        if poststaging != None and poststaging != '':
            self.driver.poststaging(poststaging)

        self.driver.close()

    def find_model(self, url_base):
        """Find device type and return appropriate class to deal with
        upgrading, version checking and else."""
        device = BaseDevice(tserver=self.tserver, **
                            self.devicedata, pkid=self.pkid)
        device.checkavailable(300)

        # Load appropriate class based on discovered device
        if any(model in device.facts["model"] for model in ("C3650", "C3850", "9300")):
            from stageit.libs.cisco.switch.iosxe import IOSXESwitch as specific_device

        elif any(model in device.facts["model"] for model in ("9200L",)):
            from stageit.libs.cisco.switch.iosxe_lite import IOSXELiteSwitch as specific_device

        elif any(model in device.facts["model"] for model in ("4221", "4321", "4331", "4351", "4431", "4451", "4461")):
            from stageit.libs.cisco.router.iosxe import IOSXERouter as specific_device

        elif any(model in device.facts["model"] for model in ("2960", "3560CX", "1841", "CDB")):
            from stageit.libs.cisco.switch.ios import IOSSwitch as specific_device

        else:
            device.close()
            raise ValueError("Unrecognised model")

        # Update database row
        data = {'status': 'In Progress'}
        requests.put(url_base + 'history/' +
                     self.pkid + URL_SUFFIX, data=data)

        device.close()
        return specific_device(**self.devicedata, tserver=self.tserver, pkid=self.pkid)

    def stageit(self, filepath, installmode, url_base, fkbootstrapconfig):
        """Do the job."""
        self.driver.checkavailable(1000)

        # Skip upgrade if file path not provided
        if filepath != '':
            try:
                self.driver.upgrade_software(uri=filepath,
                                             mode=installmode)
            except ConnectionError:
                # Connection initiates from the device back to the storage
                # If the device hasn't received an IP via DHCP on its own
                # we push a custom config and try again

                # Get bootstrap config from database
                if fkbootstrapconfig != 'null':
                    bootstrapconfig = requests.get(
                        url_base + 'bootstrapconfig/' + fkbootstrapconfig)
                    self.driver.load_bootstrap_config(**bootstrapconfig.json())
                    self.driver.upgrade_software(uri=filepath,
                                                 mode=installmode)
                else:
                    pass

        self.driver.checkavailable(50)
        self.driver.load_final_config(self.finalconfig)
        self.driver.close()


app.register_task(BaseWorker())


@app.task(bind=True, base=BaseWorker)
def baseworker(self, *args, **kwargs):
    """Call this with .delay() to start the Celery task."""
    worker = BaseWorker()
    return worker.run(fkhistory=kwargs.get('fkhistory'))
