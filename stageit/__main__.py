import yaml
import json
import queue
from flask import Flask, request, stream_with_context, Response
from time import sleep
import sys
import os

sys.path.append( os.path.join( os.path.dirname(__file__), os.path.pardir ) ) 

from libs.FakeWorker import FakeWorker
from libs.BaseWorker import BaseWorker
app = Flask(__name__)


worker_array = {}

@app.route("/log/<worker>")
def log(worker):
    def streambytes():
        oldposition = 0
        while worker_array[worker]['thread'].status != "Waiting for work":
            sleep(0.1)
            newbuffer = worker_array[worker]['thread'].driver.getlog()
            yield newbuffer[oldposition:].replace("\n","<br/>")
            oldbuffer = newbuffer
            oldposition = len(oldbuffer)

    try:
        if worker_array[worker]['thread'].status != "Waiting for work":
            return Response(stream_with_context(streambytes()))
        else:
            return "No work queued, come back later"
    except AttributeError:
        return "Discovering platform, please refresh later"

@app.route("/jobstatus/<worker>")
def jobstatus(worker):
    return worker_array[worker]['thread'].getstatus()

@app.route('/enqueue/<worker>', methods = ['POST'])
def enqueue(worker):
    queueme = request.form.copy()
    queueme['tempconfig'] = json.loads(request.form['tempconfig'])
    queueme['finalconfig'] = json.loads(request.form['finalconfig'])

    worker_array[worker]['queue'].put(queueme)
    return "OK"

if __name__ == '__main__':
    with open('stageit/term_config.yaml', 'r') as y:
        config = yaml.load(y)


    for entry in config['terminal_server']:
        server_name = "{}:{}".format(entry['hostname'], entry['port'])
        thisqueue = queue.Queue()
        if 'fake' in entry:
            server_thread = FakeWorker(thisqueue, **entry)
        else:
            server_thread = BaseWorker(thisqueue, **entry)
        server_thread.start()
        worker_array[server_name] = {
            'queue': thisqueue, 'thread': server_thread}

    app.run(threaded=True)