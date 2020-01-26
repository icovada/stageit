"""Fake worker returning Sim City 4 loading screen messages"""

import logging
import random
from time import sleep

import requests
from celery import Task

from stageit.celery import app
from stageit.libs.fakeio import FakeIO


# @app.task(bind=True)
class FakeWorker(Task):
    """
    Fake for test
    """
    name = 'stageit.libs.fake_worker.fakeworker'

    statuses = None
    historydata = None
    pkid = None
    task = None
    template = None
    work = None
    log = None

    def on_success(self, retval, task_id, args, kwargs):
        logging.info("Set task successful")
        logging.info(retval)
        logging.info(kwargs)
        requests.put('http://web:8000/api/history/' + kwargs.get('fkhistory') +
                     '/?format=json', data={'status': 'Success'})

    def on_failure(self, retval, task_id, args, kwargs):
        logging.fatal("EPIC FAIL")
        logging.fatal(retval)

    def run(self, *args, **kwargs):
        logging.info("Initializing")

        # Adapted from Sim City 4 loading screen to fit network
        self.statuses = ["Adding Maliciuous Config",
                         "Adjusting Burst Curves",
                         "Aesthesizing QoS Mappings",
                         "Aligning Fiber Connectors",
                         "Attempting to Lock Back-Buffer",
                         "Calculating Packet Loss",
                         "Calibrating Blue Lasers",
                         "Charging Capacitors",
                         "Coalescing Cloud Formations",
                         "Cohorting Templates",
                         "Compounding Inert Tessellations",
                         "Compressing Fish Files",
                         "Computing Optimal Bin Packing",
                         "Concatenating Sub-Contractors",
                         "Containing Existential Buffer",
                         "Deciding What Message to Display Next",
                         "Decomposing Singular Values",
                         "Decrementing TCAM Entries",
                         "Deleting Routes",
                         "Destabilizing Routing Protocols",
                         "Determining Width of Band",
                         "Dicing Models",
                         "Exposing Flash Variables to Streak System",
                         "Extracting Resources",
                         "Factoring Pay Scale",
                         "Fixing Stack Election Outcome Matrix",
                         "Flushing Pipe Network",
                         "Generating Jobs",
                         "Hiding Subnet Masks",
                         "Implementing Impeachment Routine",
                         "Increasing Accuracy of ACI Simulators",
                         "Increasing Automatisation",
                         "Initializing MAC Tracking Mechanism",
                         "Initializing Rhinoceros Breeding Timetable",
                         "Initializing Robotic Click-Path AI",
                         "Inserting Sublimated Messages",
                         "Integrating Curves",
                         "Integrating Desktop Form Factors",
                         "Lecturing Errant Subsystems",
                         "Mopping Occupant Leaks",
                         "Normalizing Power",
                         "Obfuscating Quigley Matrix",
                         "Overconstraining Industrial Ethernet",
                         "Perturbing Port Channels",
                         "Planting Spanning Trees",
                         "Populating Int Templates",
                         "Preparing Stacks for Random Reboots",
                         "Prioritizing Pings",
                         "Realigning Plesiosynchronous links",
                         "Reconfiguring User Mental Processes",
                         "Relaxing Splines",
                         "Removing Collision Avoidance Behavior",
                         "Removing Network Speed Bumps",
                         "Removing NTP strata",
                         "Removing Smart Licenses",
                         "Resolving GUID Conflict",
                         "Reticulating Splines",
                         "Retrieving from Back Store",
                         "Reverse Engineering STP Protocols",
                         "Routing Neural Network Infrastructure",
                         "Scattering Rhino Food Sources",
                         "Scratching Chassis",
                         "Screwing rack mounts",
                         "Sequencing Particles",
                         "Setting Inner Deity Indicators",
                         "Setting Universal Physical Constants",
                         "Splatting Transforms",
                         "Stratifying PCBs",
                         "Sub-Sampling Data",
                         "Synthesizing Packets",
                         "Time-Compressing Simulator Clock",
                         "Unable to Reveal Current Activity",
                         "Upgrading Macrocode",
                         "Weaving Data Fabrics",
                         "Zeroing nvram"]

        logging.info("Fake Worker ready")
        logging.info(kwargs.get('fkhistory'))

        self.historydata = requests.get(
            'http://web:8000/api/history/' + kwargs.get('fkhistory') + '/?format=json')
        if self.historydata.json().get('workerid') is not None:
            raise AssertionError(
                "Task already being worked on by someone else")

        requests.put('http://web:8000/api/history/' + kwargs.get('fkhistory') + '/?format=json',
                     data={'workerid': kwargs.get('celeryid'), 'status': 'In Progress'})

        self.pkid = self.historydata.json().get('pkid')
        fktask = self.historydata.json().get('fktask')

        self.task = requests.get(
            'http://web:8000/api/task/' + fktask + '/?format=json')
        fktemplate = self.task.json().get('fktemplate')
        self.template = requests.get(
            'http://web:8000/api/template/' + fktemplate + '/?format=json')

        logging.info(self.template.json().get('template'))

        self.work = kwargs.get('work')

        self.log = FakeIO(fkhistory=self.pkid)
        self.stageit()

    def driver(self):
        """
        Return complete log.

        Subroutine because emulates an import in BaseWorker
        """

        def getlog(self):
            return self.log.getvalue().decode('utf-8')

    def stageit(self):
        """Choose random status"""
        for i in range(random.randint(30, 30)):
            status = self.statuses[random.randint(0, len(self.statuses)-1)]
            self.log.write(status.encode('utf-8') + "\n".encode('utf-8'))
            if (i % 2) == 0:
                self.log.flush()
            logging.info(status)
            sleep(random.randint(1, 2))

        self.log.flush()
        return True


app.register_task(FakeWorker())


@app.task(bind=True, base=FakeWorker)
def fakeworker(self, **kwargs):
    celeryid = self.request.id.__str__()
    worker = FakeWorker()
    return worker.run(fkhistory=kwargs.get('fkhistory'), celeryid=celeryid)
