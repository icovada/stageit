"""Fake worker returning Sim City 4 loading screen messages"""

from time import sleep
import random
import io
#from uuid import uuid4
import pickle
#from stageit.libs.db import History, newsession
import logging
from stageit.libs.fakeio import FakeIO
from stageit.celery import app
import requests

class FakeWorker(app.Task):
    """
    Fake for test
    """
    name = 'stageit.libs.fake_worker'

    def __init__(self, **kwargs):
        self.status = "Initializing"

        # Adapted from Sim City 4 loading screen to fit network
        self.statuses = ["Adding Hidden Config",
                         "Adjusting Burst Curves",
                         "Aesthesizing QoS Mappings",
                         "Aligning Covariance Matrices",
                         "Asserting Packet Exemplars",
                         "Attempting to Lock Back-Buffer",
                         "Binding Spanning Root System",
                         "Building Data Trees",
                         "Calculating Inverse Probability Matrices",
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
                         "Downloading Satellite Terrain Data",
                         "Exposing Flash Variables to Streak System",
                         "Extracting Resources",
                         "Factoring Pay Scale",
                         "Fixing Stack Election Outcome Matrix",
                         "Flushing Pipe Network",
                         "Generating Jobs",
                         "Hiding Willio Subnet Mask",
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
                         "Perturbing Matrices",
                         "Populating Int Templates",
                         "Preparing Stacks for Random Reboots",
                         "Prioritizing Pings",
                         "Realigning Plesiosynchronous links",
                         "Reconfiguring User Mental Processes",
                         "Relaxing Splines",
                         "Removing Network Speed Bumps",
                         "Removing Collision Avoidance Behavior",
                         "Resolving GUID Conflict",
                         "Reticulating Splines",
                         "Removing NTP strata",
                         "Retrieving from Back Store",
                         "Reverse Engineering STP Protocols",
                         "Routing Neural Network Infanstructure",
                         "Scattering Rhino Food Sources",
                         "Screwing rack mounts",
                         "Scratching Chassis",
                         "Sequencing Particles",
                         "Setting Inner Deity Indicators",
                         "Setting Universal Physical Constants",
                         "Splatting Transforms",
                         "Stratifying PCBs",
                         "Sub-Sampling Data",
                         "Synthesizing Packets",
                         "Time-Compressing Simulator Clock",
                         "Unable to Reveal Current Activity",
                         "Zeroing nvram"]

        self.work = None
        self.session = None
        self.dbrow = None
        self.log = None

    def run(self, **kwargs):
        logging.info("Fake Worker ready")
        logging.info(kwargs.get('fkhistory'))

        self.historydata = requests.get('http://localhost:8000/api/history/' + kwargs.get('fkhistory') + '/?format=json')
        self.pkid = self.historydata.json().get('pkid')
        fktask = self.historydata.json().get('fktask')

        self.task = requests.get('http://localhost:8000/api/tasks/' + fktask + '/?format=json')
        fktemplate = self.task.json().get('fktemplate')
        self.template = requests.get('http://localhost:8000/api/templates/' + fktemplate + '/?format=json')

        logging.info(self.template.json().get('template'))
        
        self.work = kwargs.get('work')

        self.log = FakeIO(fkhistory=self.pkid)
        return self.stageit()

    def getstatus(self):
        """Return status of running task"""
        return self.status

    def driver(self):
        """
        Return complete log.

        Subroutine because emulates an import in BaseWorker
        """
        def getlog(self):
            return self.log.getvalue().decode('utf-8')

    def stageit(self):
        """Choose random status"""
        for i in range(random.randint(5, 10)):
            self.status = self.statuses[random.randint(0, len(self.statuses)-1)]
            self.log.write(self.status.encode('utf-8') + "\n".encode('utf-8'))
            if (i % 2) == 0:
                self.log.flush()
            logging.info(self.status)
            sleep(random.randint(1, 10))
        
        self.log.flush()
        return True
        

@app.task()
def fakeworker(**kwargs):
    worker = FakeWorker()
    return worker.run(fkhistory = kwargs.get('fkhistory'))
