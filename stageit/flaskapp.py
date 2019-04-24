from werkzeug.serving import run_simple
from flask import Flask, request, stream_with_context, Response, render_template, abort, jsonify
from flask.logging import default_handler
import config
from time import sleep
import json
import yaml
import os
from jinja2 import Environment, BaseLoader
import jinja2
from uuid import uuid4 as uuid
import libs.db as db
import pickle
from sqlalchemy.sql.expression import select
from uuid import uuid4 as uuid

APP_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(APP_PATH, 'stageit/web/templates')

app = Flask(__name__, template_folder=TEMPLATE_PATH)


@app.route("/")
def home():
    return render_template("layout.html")


@app.route("/workers")
def workers():
    text = render_template("workers.html", workers=config.worker_array)
    return text


@app.route("/tasks")
def tasks():
    templatecolumns = db.templates.columns
    query = select((templatecolumns['id'],
                    templatecolumns['name'],
                    templatecolumns['platform']))
    res = db.conn.execute(query)
    allrows = res.fetchall()

    return render_template("tasks.html", header=("Id", "Name", "Platform"), table=allrows)


@app.route("/tasks/<taskid>")
def taskdetail(taskid):
    return render_template("tasks/taskdetail.html")


@app.route("/templates/add")
def templates():
    return render_template("addtemplates.html")


@app.route("/modal")
def modal():
    return render_template("test/modal.html")


@app.route("/api/addtemplate", methods=['POST'])
def apiaddtemplate():
    argdict = request.form.copy()
    argdict['id'] = str(uuid())
    del argdict['templatevalues']
    argdict['templatevalues'] = pickle.dumps(yaml.load(request.form['templatevalues']))
    print("VARS")
    print(argdict)
    ins = db.templates.insert().values(**argdict)
    db.conn.execute(ins)
    return argdict['id']


@app.route("/convertjinja", methods=['POST'])
def convertjinja():
    try:
        rtemplate = Environment(loader=BaseLoader).from_string(
            request.form["template"])
    except jinja2.exceptions.TemplateSyntaxError as e:
        return jsonify({'status':'Error', 'message':str(e)})

    yamlvalues = yaml.load(request.form["values"])
    if yamlvalues is None:
        yamlvalues = {}
    
    result = {'status':'OK', 'message': rtemplate.render(**yamlvalues).replace("\n", "<br/>")}
    return jsonify(result)


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
