import yaml
from libs.FakeWorker import FakeWorker
import queue

if __name__ == '__main__':
    with open('term_config.yaml', 'r') as y:
        config = yaml.load(y)

    worker_array = {}

    for entry in config['terminal_server']:
        server_name = "{}:{}".format(entry['hostname'], entry['port'])
        thisqueue = queue.Queue()
        server_thread = FakeWorker(thisqueue, **entry)
        server_thread.start()
        worker_array[server_name] = {
            'queue': thisqueue, 'thread': server_thread}
