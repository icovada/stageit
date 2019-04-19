from werkzeug.serving import run_simple
from flask import Flask, request, stream_with_context, Response, render_template
from flask.logging import default_handler
import config
from time import sleep
import json

app = Flask(__name__)
app.logger.removeHandler(default_handler)


@app.route("/log/<worker>")
def log(worker):
    def streambytes():
        oldposition = 0
        while config.worker_array[worker]['thread'].status != "Waiting for work":
            sleep(0.1)
            newbuffer = config.worker_array[worker]['thread'].driver.getlog()
            yield newbuffer[oldposition:].replace("\n", "<br/>")
            oldbuffer = newbuffer
            oldposition = len(oldbuffer)

    try:
        if config.worker_array[worker]['thread'].status != "Waiting for work":
            return Response(stream_with_context(streambytes()))
        else:
            return "No work queued, come back later"
    except AttributeError:
        return "Discovering platform, please refresh later"


@app.route("/jobstatus/<worker>")
def jobstatus(worker):
    print(config.worker_array)
    return config.worker_array[worker]['thread'].getstatus()


@app.route('/enqueue/<worker>', methods=['POST'])
def enqueue(worker):
    queueme = request.form.copy()
    queueme['tempconfig'] = json.loads(request.form['tempconfig'])
    queueme['finalconfig'] = json.loads(request.form['finalconfig'])

    config.worker_array[worker]['queue'].put(queueme)
    return "OK"


def run():
    run_simple('127.0.0.1', 5000, app)
