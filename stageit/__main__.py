"""
StageIT

Stage network devices
"""

import logging
import queue
import sys
import os
import yaml

sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir)) 

from stageit.libs.fake_worker import FakeWorker
from stageit.libs.base_worker import BaseWorker

import config


def main():
    """Main. What else."""
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(threadName)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M')
    with open('stageit/term_config.yaml', 'r') as term_yaml:
        configuration = yaml.safe_load(term_yaml)

    for entry in configuration['serials']:
        server_name = "{}:{}".format(entry['hostname'], entry['port'])

        this_queue = queue.Queue()

        # Get terminal server management
        cserver = configuration['console_server'][entry['hostname']]
        if cserver['model'] == 'cisco':
            from stageit.libs.consoleserver.cisco import CiscoConsoleServer
            cservermgmt = CiscoConsoleServer(hostname=entry['hostname'],
                                             line=entry['line'],
                                             **cserver)
        else:
            from stageit.libs.consoleserver import BaseConsoleServer
            cservermgmt = BaseConsoleServer(hostname=entry['hostname'],
                                            **cserver)

        # Create worker subprocess
        if entry['hostname'] == 'fake':
            server_thread = FakeWorker(queue, **entry)
        else:
            server_thread = BaseWorker(this_queue, cservermgmt, **entry)

        # Start workers
        server_thread.start()
        logging.debug("Started thread for %s:%s", entry['hostname'], entry['port'])
        config.WORKER_DICT[server_name] = {
            'queue': this_queue, 'thread': server_thread}


if __name__ == '__main__':
    import stageit.web.app as app

    main()
    app.run()
