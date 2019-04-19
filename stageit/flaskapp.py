from werkzeug.serving import run_simple
from flask import Flask, request, stream_with_context, Response, render_template
from flask.logging import default_handler
import config
from time import sleep
import json
import os

APP_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(APP_PATH, 'stageit/web/templates')

app = Flask(__name__, template_folder=TEMPLATE_PATH)


@app.route("/")
def home():
    return render_template("layout.html")


@app.route("/workers")
def workers():
    return render_template("workers.html")


@app.route("/tasks")
def tasks():
    return render_template("tasks.html")

@app.route("/tasks/<taskid>")
def taskdetail(taskid):
    return render_template("tasks/taskdetail.html")


@app.route("/templates")
def templates():
    return render_template("templates.html")


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
