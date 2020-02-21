"""Base Worker thread from which BaseDevice is spawned."""

import logging
from datetime import datetime

import requests
from jinja2 import BaseLoader, Environment

from libs.base_device import BaseDevice
from libs.netio import NetIO

URL_SUFFIX = "/?format=json"


class BaseWorker():
    """Base class to connect to network device."""

    workerid = None
    pkid = None
    logbuffer = None
    historydata = None
    fktask = None
    taskdata = None
    templatedata = None
    serialportdata = None
    terminalserverdata = None
    template = None
    finalconfig = None
    devicedata = None
    tempconfig = None
    tserver = None
    driver = None


    def __init__(self, *args, **kwargs):
        """Celery calls this to start the task."""

        self.historydata = kwargs.get('historydata')
        self.endpoint = kwargs.get('endpoint')
        self.worker_id = kwargs.get('worker_id')
        self.pkid = self.historydata['pkid']

        self.logbuffer = NetIO(fkhistory=self.pkid, endpoint=self.endpoint)
        logging.info('Worker for %s ready', self.pkid)

        if self.historydata['workerid'] is not None:
            raise AssertionError(
                "Task already being worked on by someone else")
        
        try:
            # Mark History row as being worked on by us
            data = {'workerid': self.worker_id,
                    'status': 'Discovering'}
            requests.put(self.endpoint + '/api/history/' +
                         self.pkid + URL_SUFFIX, data=data)

            # Now we have checked the task is OK to work on and marked it as ours, fetch task data
            self.fktask = self.historydata['fktask']
            self.taskdata = requests.get(
                self.endpoint + '/api/task/' + self.fktask + URL_SUFFIX).json()

            # From the task we find the template
            fktemplate = self.taskdata.get('fktemplate')
            self.templatedata = requests.get(
                self.endpoint + '/api/template/' + fktemplate + URL_SUFFIX).json()

            # Find the port to connect to
            self.serialportdata = requests.get(
                self.endpoint + '/api/serialport/' + self.historydata.get('fkserialport') + URL_SUFFIX).json()

            # Find the terminal server to connect to
            self.terminalserverdata = requests.get(
                self.endpoint + '/api/terminalserver/' + self.serialportdata.get('fkterminalserver') + URL_SUFFIX).json()
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
            platform = 'ios'
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

            # Find driver for Terminal Server
            if self.terminalserverdata.get('model') == 'cisco':
                from libs.consoleserver.cisco import CiscoConsoleServer as tserver
            else:
                from libs.consoleserver import BaseConsoleServer as tserver

            # Instantiate terminal server class
            self.tserver = tserver(
                **{**self.serialportdata, **self.terminalserverdata})

            logging.info('Discovering platform')
            self.driver = self.find_model(self.endpoint)

            # Actually do the job (finally!)
            self.stageit(filepath=filepath, installmode=installmode,
                        fkbootstrapconfig=self.templatedata.get('fkbootstrapconfig'))

            if poststaging is not None and poststaging != '':
                self.driver.poststaging(poststaging)

            self.driver.close()
            
            self.on_success(self.pkid)
        except Exception as e:
            self.on_failure(self.pkid, e)


    def on_success(self, fkhistory):
        """
        Celery runs this if the task runs successfully
        Update database, set history as successful and delete task.
        """
        logging.info("Set task successful")
        logging.info(retval)
        logging.info(kwargs)

        requests.delete(self.endpoint + '/api/templates/' + self.fktask + URL_SUFFIX)
        data = {'status': 'Completed',
                'dateend': datetime.utcnow()
                }
        requests.put(self.endpoint + '/api/history/' + self.pkid + URL_SUFFIX, data=data)

    def on_failure(self, fkhistory, exception):
        """
        Celery runs this if the task fails
        Update database, set history as failed.
        """

        logging.error("EPIC FAIL")
        logging.info(retval)
        data = {'status': 'Fail',
                'dateend': datetime.utcnow()
                }
        requests.put(self.endpoint + '/api/history/' + self.pkid + URL_SUFFIX, data=data)

    def find_model(self, url_base):
        """Find device type and return appropriate class to deal with
        upgrading, version checking and else."""
        device = BaseDevice(tserver=self.tserver, endpoint=self.endpoint, **
                            self.devicedata, pkid=self.pkid)
        device.checkavailable(300)

        # Load appropriate class based on discovered device
        if any(model in device.facts["model"] for model in ("C3650", "C3850", "9300")):
            from libs.cisco.switch.iosxe import IOSXESwitch as specific_device

        elif any(model in device.facts["model"] for model in ("9200L",)):
            from libs.cisco.switch.iosxe_lite import IOSXELiteSwitch as specific_device

        elif any(model in device.facts["model"] for model in ("4221", "4321", "4331", "4351", "4431", "4451", "4461")):
            from libs.cisco.router.iosxe import IOSXERouter as specific_device

        elif any(model in device.facts["model"] for model in ("2960", "3560CX", "1841", "CDB")):
            from libs.cisco.switch.ios import IOSSwitch as specific_device

        else:
            device.close()
            raise ValueError("Unrecognised model")

        # Update database row
        data = {'status': 'In Progress'}
        requests.put(url_base + '/api/history/' +
                     self.pkid + URL_SUFFIX, data=data)

        device.close()
        return specific_device(**self.devicedata, tserver=self.tserver, pkid=self.pkid)

    def stageit(self, filepath, installmode, fkbootstrapconfig):
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
                        self.endpoint + '/api/bootstrapconfig/' + fkbootstrapconfig)
                    self.driver.load_bootstrap_config(**bootstrapconfig.json())
                    self.driver.upgrade_software(uri=filepath,
                                                 mode=installmode)
                else:
                    pass

        self.driver.checkavailable(50)
        self.driver.load_final_config(self.finalconfig)
        self.driver.close()
