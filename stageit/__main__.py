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

    for entry in configuration['serials']:
        server_name = "{}:{}".format(entry['hostname'], entry['port'])

        q = queue.Queue()

        # Get terminal server management
        cserver = configuration['console_server'][entry['hostname']]
        if cserver['model'] == 'cisco':
            from stageit.libs.consoleserver.cisco import CiscoConsoleServer
            cservermgmt = CiscoConsoleServer(hostname=entry['hostname'], line=entry['line'], **cserver)
        else: 
            from stageit.libs.consoleserver import BaseConsoleServer
            cservermgmt = BaseConsoleServer(hostname=entry['hostname'], **cserver)

        # Create worker subprocess
        if entry['hostname'] == 'fake':
            server_thread = FakeWorker(queue, **entry)
        else:
            server_thread = BaseWorker(q, cservermgmt, **entry)

        # Start workers
        server_thread.start()
        logging.debug("Started thread for {}:{}".format(
            entry['hostname'], entry['port']))
        config.worker_array[server_name] = {
            'queue': q, 'thread': server_thread}


if __name__ == '__main__':
    import stageit.web.app as app
    
    main()
    app.run()