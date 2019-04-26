import logging
import sys
import os
import yaml
import json
import queue

sys.path.append( os.path.join( os.path.dirname(__file__), os.path.pardir ) ) 
from libs.FakeWorker import FakeWorker
from libs.BaseWorker import BaseWorker
import config


def main():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(threadName)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M')
    with open('stageit/term_config.yaml', 'r') as y:
        configuration = yaml.safe_load(y)

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


if __name__ == '__main__':
    import flaskapp
    
    main()
    flaskapp.run()