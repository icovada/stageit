import yaml
import json
import queue
from time import sleep
import sys
import os
import sqlalchemy
from libs.FakeWorker import FakeWorker
from libs.BaseWorker import BaseWorker
import flaskapp
import config

sys.path.append( os.path.join( os.path.dirname(__file__), os.path.pardir ) ) 

if __name__ == '__main__':
    with open('stageit/term_config.yaml', 'r') as y:
        config = yaml.load(y)

    engine = sqlalchemy.create_engine('sqlite:///:memory:', echo=True)

    for entry in config['terminal_server']:
        server_name = "{}:{}".format(entry['hostname'], entry['port'])
        thisqueue = queue.Queue()
        if entry['hostname'] == 'fake':
            server_thread = FakeWorker(thisqueue, **entry)
        else:
            server_thread = BaseWorker(thisqueue, **entry)
        server_thread.start()
        config.worker_array[server_name] = {
            'queue': thisqueue, 'thread': server_thread}

    flaskapp.run()