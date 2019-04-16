import yaml
from libs.FakeWorker import FakeWorker
import queue
from flask import Flask, request, stream_with_context, Response
from time import sleep
app = Flask(__name__)


worker_array = {}

@app.route("/<worker>")
def getlog(worker):
    def streambytes():
        oldposition = 0
        while worker_array[worker]['thread'].status != "Waiting for work":
            sleep(0.1)
            newbuffer = worker_array[worker]['thread'].getlog()
            yield newbuffer[oldposition:].replace("\n","<br/>")
            oldbuffer = newbuffer
            oldposition = len(oldbuffer)

    return Response(stream_with_context(streambytes()))

@app.route('/enqueue/<worker>', methods = ['POST'])
def enqueue(worker):
    worker_array[worker]['queue'].put(request.form['data'])
    return "OK"

if __name__ == '__main__':
    with open('term_config.yaml', 'r') as y:
        config = yaml.load(y)


    for entry in config['terminal_server']:
        server_name = "{}:{}".format(entry['hostname'], entry['port'])
        thisqueue = queue.Queue()
        server_thread = FakeWorker(thisqueue, **entry)
        server_thread.start()
        worker_array[server_name] = {
            'queue': thisqueue, 'thread': server_thread}

    app.run(threaded=True)