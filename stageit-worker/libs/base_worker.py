"""Base Worker thread from which BaseDevice is spawned."""

import logging
from datetime import datetime

import requests
from jinja2 import BaseLoader, Environment

from libs.base_device import BaseDevice
from libs.netio import NetIO


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
        self.headers = kwargs.get('headers')

        if self.historydata['workerid'] is not None:
            raise AssertionError(
                "Task already being worked on by someone else")

        self.logbuffer = NetIO(fkhistory=self.pkid, endpoint=self.endpoint, headers=self.headers)
        logging.info('Worker for %s ready', self.pkid)

        try:
            # Mark History row as being worked on by us
            historydata = requests.get(
                f'{self.endpoint}/api/history/{self.pkid}/?format=json', headers=self.headers).json()
            historydata['workerid'] = self.worker_id
            historydata['status'] = 'Discovering'
            logging.debug('Retrieving history data')
            requests.put(
                f'{self.endpoint}/api/history/{self.pkid}/?format=json', data=historydata, headers=self.headers)

            # Now we have checked the task is OK to work on and marked it as ours, fetch task data
            self.fktask = self.historydata['fktask']
            logging.debug('Retrieving task data')
            self.taskdata = requests.get(
                f'{self.endpoint}/api/task/{self.fktask}/?format=json', headers=self.headers).json()

            # From the task we find the template
            fktemplate = self.taskdata.get('fktemplate')
            logging.debug('Retrieving template data')
            self.templatedata = requests.get(
                f'{self.endpoint}/api/template/{fktemplate}/?format=json', headers=self.headers).json()

            # Find the port to connect to
            fkserialport = self.historydata.get('fkserialport')
            logging.debug('Retrieving serial port data')
            self.serialportdata = requests.get(
                f'{self.endpoint}/api/serialport/{fkserialport}/?format=json', headers=self.headers).json()

            # Find the terminal server to connect to
            fkterminalserver = self.serialportdata.get('fkterminalserver')
            logging.debug('Retrieving terminal server data')
            self.terminalserverdata = requests.get(
                f'{self.endpoint}/api/terminalserver/{fkterminalserver}/?format=json', headers=self.headers).json()
            logging.info('Successfully retrieved all data')

            hostname = self.terminalserverdata.get('hostname')
            port = self.serialportdata.get('port')
            transport = self.serialportdata.get('transport')
            username = self.terminalserverdata.get('username')
            password = self.terminalserverdata.get('password')

            description = self.taskdata.get('description')
            taskvalues = self.taskdata.get('taskvalues')
            self.template = self.templatedata.get('template')
            rtemplate = Environment(
                loader=BaseLoader).from_string(self.template)
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
                logging.debug('Terminal server driver: CiscoConsoleServer')
                from libs.consoleserver.cisco import CiscoConsoleServer as tserver
            else:
                logging.debug('Terminal server driver: BaseConsoleServer')
                from libs.consoleserver import BaseConsoleServer as tserver

            # Instantiate terminal server class
            logging.debug('Instantiate terminal server class')
            self.tserver = tserver(
                **{**self.serialportdata, **self.terminalserverdata})

            logging.info('Discovering platform')
            self.driver = self.find_model(self.endpoint)

            # Actually do the job (finally!)
            logging.info('Running main stageit routine')
            self.stageit(filepath=filepath, installmode=installmode,
                         fkbootstrapconfig=self.templatedata.get('fkbootstrapconfig'))

            if poststaging is not None and poststaging != '':
                logging.info('Starting poststaging routine')
                self.driver.poststaging(poststaging)

            logging.info('Task complete')
            self.driver.close()

            self.on_success(self.pkid)
        except Exception as e:
            self.on_failure(e)
            raise e

        self.on_success()

    def on_success(self):
        """
        Celery runs this if the task runs successfully
        Update database, set history as successful and delete task.
        """
        logging.info("Set task successful")

        requests.delete(
            f'{self.endpoint}/api/task/{self.fktask}', headers=self.headers)

        historydata = requests.get(
            f'{self.endpoint}/api/history/{self.pkid}/?format=json', headers=self.headers).json()
        historydata['status'] = 'Completed'
        historydata['dateend'] = datetime.utcnow()
        requests.put(
            f'{self.endpoint}/api/history/{self.pkid}/?format=json', data=historydata, headers=self.headers)

        self.logbuffer.close()

    def on_failure(self, exception):
        """
        Celery runs this if the task fails
        Update database, set history as failed.
        """

        logging.error("EPIC FAIL")
        historydata = requests.get(
            f'{self.endpoint}/api/history/{self.pkid}/?format=json', headers=self.headers).json()
        historydata['status'] = 'Fail'
        historydata['dateend'] = datetime.utcnow()
        requests.put(
            f'{self.endpoint}/api/history/{self.pkid}/?format=json', data=historydata, headers=self.headers)
        self.logbuffer.write(str(exception).encode('utf-8'))
        self.logbuffer.close()

    def find_model(self, url_base):
        """Find device type and return appropriate class to deal with
        upgrading, version checking and else."""
        logging.debug('Instantiating BaseDevice driver')
        device = BaseDevice(tserver=self.tserver, endpoint=self.endpoint, pkid=self.pkid, headers=self.headers, **self.devicedata)
        logging.info('Discovering model')
        device.checkavailable(300)

        logging.debug('Discovered model: %s', device.facts['model'])
        # Load appropriate class based on discovered device
        if any(model in device.facts["model"] for model in ("C3650", "C3850", "9300", "9400", "9500", "9600")):
            logging.debug('Using IOSXESwitch driver')
            from libs.cisco.switch.iosxe import IOSXESwitch as specific_device

        elif any(model in device.facts["model"] for model in ("9200L",)):
            logging.debug('Using IOSXELiteSwitch driver')
            from libs.cisco.switch.iosxe_lite import IOSXELiteSwitch as specific_device

        elif any(model in device.facts["model"] for model in ("4221", "4321", "4331", "4351", "4431", "4451", "4461")):
            logging.debug('Using IOSXERouter driver')
            from libs.cisco.router.iosxe import IOSXERouter as specific_device

        elif any(model in device.facts["model"] for model in ("2960", "3560CX", "1841", "CDB")):
            logging.debug('Using IOSSwitch driver')
            from libs.cisco.switch.ios import IOSSwitch as specific_device

        else:
            device.close()
            logging.error("Unrecognised model")
            raise ValueError("Unrecognised model")

        # Update database row
        historydata = requests.get(
            f'{self.endpoint}/api/history/{self.pkid}/?format=json', headers=self.headers).json()
        historydata['status'] = 'In Progress'
        logging.debug('Updating history, status: In Progress')
        requests.put(
            f'{url_base}/api/history/{self.pkid}/?format=json', data=historydata, headers=self.headers)

        device.close()
        return specific_device(**self.devicedata, tserver=self.tserver, endpoint=self.endpoint, pkid=self.pkid, headers=self.headers)

    def stageit(self, filepath, installmode, fkbootstrapconfig):
        """Do the job."""
        logging.debug('Checking availability of device with new driver')
        self.driver.checkavailable(1000)

        # Skip upgrade if file path not provided
        if filepath != '':
            logging.debug('url not empty, starting upgrade')
            try:
                self.driver.upgrade_software(uri=filepath,
                                             mode=installmode)
            except ConnectionError:
                logging.warning('Device has no IP, loading bootstrap config')
                # Connection initiates from the device back to the storage
                # If the device hasn't received an IP via DHCP on its own
                # we push a custom config and try again

                # Get bootstrap config from database
                if fkbootstrapconfig != 'null':
                    logging.debug('Retrieving bootstrap config')
                    bootstrapconfig = requests.get(
                        self.endpoint + '/api/bootstrapconfig/' + fkbootstrapconfig, headers=self.headers)
                    self.driver.load_bootstrap_config(**bootstrapconfig.json())
                    self.driver.upgrade_software(uri=filepath,
                                                 mode=installmode)
                else:
                    pass

        self.driver.checkavailable(50)
        self.driver.load_final_config(self.finalconfig)
        self.driver.close()
