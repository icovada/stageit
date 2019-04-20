import logging
import sys
import os
sys.path.append( os.path.join( os.path.dirname(__file__), os.path.pardir ) ) 

import yaml
import json
import queue
from time import sleep
import sqlalchemy
from libs.FakeWorker import FakeWorker
from libs.BaseWorker import BaseWorker
import flaskapp
import config

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(threadName)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M')
    with open('stageit/term_config.yaml', 'r') as y:
        configuration = yaml.safe_load(y)

    engine = sqlalchemy.create_engine('sqlite:///:memory:', echo=True)

    for entry in configuration['terminal_server']:
        server_name = "{}:{}".format(entry['hostname'], entry['port'])
        thisqueue = queue.Queue()
        if entry['hostname'] == 'fake':
            server_thread = FakeWorker(thisqueue, **entry)
        else:
            server_thread = BaseWorker(thisqueue, **entry)
        server_thread.start()
        logging.debug("Started thread for {}:{}".format(
            entry['hostname'], entry['port']))
        config.worker_array[server_name] = {
            'queue': thisqueue, 'thread': server_thread}

    flaskapp.run()
