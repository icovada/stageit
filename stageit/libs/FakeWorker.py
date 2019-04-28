from threading import Thread
import queue
from time import sleep
from io import BytesIO
import logging
import random
import io


class FakeWorker(Thread):
    """
    Fake for test
    """

    def __init__(self, q, **kwargs):
        Thread.__init__(self)
        self.q = q
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

    def run(self):
        logging.info("Fake Worker ready")
        while True:
            try:
                self.status = "Waiting for work"
                self.work = self.q.get(timeout=600)

            except queue.Empty:
                self.status = "Dead"
                return

            self.log = io.BytesIO()
            self.stageit()
            self.q.task_done()

    def getstatus(self):
        return self.status

    def stageit(self):
        for i in range(random.randint(5, 60)):
            self.status = self.statuses[random.randint(0, len(self.statuses)-1)]
            self.log.write(self.status.encode('utf-8'))
            sleep(random.randint(1, 10))
