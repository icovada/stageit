from werkzeug.serving import run_simple
from flask import Flask, request, stream_with_context, Response, render_template, abort, jsonify, redirect, url_for
from flask.logging import default_handler
import config
from time import sleep
import json
import yaml
import os
from jinja2 import Environment, BaseLoader
import jinja2
from uuid import uuid4 as uuid
from stageit.libs.db import Templates, History, Tasks, newsession
import pickle

APP_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(APP_PATH, 'web')

app = Flask(__name__, template_folder=TEMPLATE_PATH)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

# User Interface


@app.route("/")
def home():
    return render_template("templates/layout.html")


@app.route("/workers")
def workers():
    text = render_template("templates/workers.html",
                           workers=config.worker_array)
    return text


@app.route("/templates")
def templates():
    session = newsession()
    templates = session.query(Templates.pkid,
                              Templates.name,
                              Templates.description)

    return render_template("templates/templates.html",
                           header=("Name", "Description"),
                           table=templates.all())


@app.route("/tasks")
def tasks():
    session = newsession()
    tasks = session.query(Tasks.pkid,
                          Tasks.fktemplate,
                          Tasks.description)

    return render_template("templates/tasks.html",
                           header=("ID", "Template", "Description"),
                           table=tasks.all(),
                           workers=config.worker_array.keys())


@app.route("/templates/<templateid>")
def templatedetail(templateid):
    session = newsession()
    template = session.query(Templates).get(templateid)
    templatedict = template.__dict__

    if template.templatevalues is not None:
        templatedict['templatevalues'] = yaml.dump(pickle.loads(template.templatevalues))
    else: 
        templatedict['templatevalues'] = ''

    return render_template('templates/templates/detail.html', **templatedict)


@app.route("/templates/add")
def templatesadd():
    return render_template("templates/templates/add.html")


@app.route("/tasks/add")
def createtask():
    fktemplate = request.args.get('fktemplate')
    session = newsession()
    template = session.query(Templates).get(fktemplate)
    templatedict = template.__dict__

    if template.templatevalues is not None:
        templatedict['templatevalues'] = yaml.dump(pickle.loads(template.templatevalues))
    else: 
        templatedict['templatevalues'] = ''

    return render_template("templates/tasks/add.html", fktemplate=fktemplate, **templatedict)


@app.route("/tasks/<taskid>")
def taskdetail(taskid):
    session = newsession()
    task = session.query(Tasks).get(taskid)
    taskdict = task.__dict__

    return render_template('templates/tasks/detail.html', **taskdict)


# API


@app.route('/tasks/<worker>/<taskid>')
def enqueue(worker, taskid):
    session = newsession()
    task = session.query(Tasks).filter(Tasks.pkid == taskid).one()
    taskdict = task.__dict__

    template = session.query(Templates).filter(
        Templates.pkid == taskdict['fktemplate'])
    templatedict = template.one().__dict__

    try:
        rtemplate = Environment(loader=BaseLoader).from_string(
            templatedict['template'])
    except jinja2.exceptions.TemplateSyntaxError as e:
        return jsonify({'status': 'Error', 'message': str(e)})

    taskvalues = pickle.loads(templatedict['taskvalues'])
    if taskvalues is not None:
        taskvalues = yaml.dump(taskvalues)
    
    taskdict['taskvalues'] = taskvalues

    finalconfig = rtemplate.render(
        pickle.loads(taskdict['taskvalues'])).split("\n")

    queueme = templatedict
    queueme['finalconfig'] = finalconfig
    config.worker_array[worker]['queue'].put(queueme)
    return "OK"


@app.route("/templates/<templateid>/add", methods=['POST'])
def templatemanager(templateid):
    session = newsession()
    template = session.query(Templates).get(templateid)
    templatedict = template.__dict__

    picklevalues = pickle.dumps(yaml.load(request.form['taskvalues']))

    task = Tasks(pkid=str(uuid()),
                 taskvalues=picklevalues,
                 description=request.form['description'],
                 fktemplate=templatedict['pkid'])

    session.add(task)
    session.commit()
    return redirect('/tasks/' + templateid, code=302)


@app.route("/api/templates", methods=['POST'])
def apiaddtemplate():
    session = newsession()
    argdict = request.form.to_dict()
    argdict['pkid'] = str(uuid())

    templatevalues = yaml.load(request.form['templatevalues'])
    if templatevalues is not None:
        templatevalues = pickle.dumps(templatevalues)

    argdict['templatevalues'] = templatevalues

    template = Templates(**argdict)

    session.add(template)
    session.commit()
    return argdict['pkid']


@app.route("/api/templates/<pkid>", methods=['PUT'])
def apiupdatetemplate(pkid):
    session = newsession()

    template = session.query(Templates).get(pkid)
    # Check the template is not associated with pending tasks
    if len(template.tasks) != 0:
        raise InvalidUsage("Pending tasks assigned", 409)

    argdict = request.form.to_dict()

    templatevalues = yaml.load(request.form['templatevalues'])
    if templatevalues is not None:
        templatevalues = pickle.dumps(templatevalues)

    argdict['templatevalues'] = templatevalues

    for key, value in argdict.items():
        setattr(template, key, value)

    session.commit()
    return "ok"


@app.route("/api/templates/<pkid>", methods=['DELETE'])
def apideletetemplate(pkid):
    session = newsession()
    template = session.query(Templates).get(pkid)
    session.delete(template)
    try:
        session.commit()
    except:
        raise InvalidUsage("Template used by one or more tasks", 412)

    return "OK"


@app.route("/api/tasks", methods=['POST'])
def apiaddtask():
    session = newsession()
    argdict = request.form.to_dict()

    argdict['pkid'] = str(uuid())

    if request.form['taskvalues'] == '':
        taskvalues = None
    else:
        yamlconfig = yaml.load(request.form['taskvalues'])
        if (argdict['description'] == '' and 'hostname' not in yamlconfig):
            raise InvalidUsage("Missing description")
        else:
            taskvalues = pickle.dumps(yamlconfig)
            if 'hostname' in yamlconfig:
                argdict['description'] = yamlconfig['hostname']


    argdict['taskvalues'] = taskvalues

    task = Tasks(**argdict)

    session.add(task)
    session.commit()
    return argdict['pkid']


@app.route("/api/tasks/<pkid>", methods=['DELETE'])
def apideletetask(pkid):
    session = newsession()
    task = session.query(Tasks).get(pkid)
    session.delete(task)
    try:
        session.commit()
    except:
        raise InvalidUsage("Failed", 412)

    return "OK"


# Backend

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


# AJAX

@app.route("/api/convertjinja", methods=['POST'])
def convertjinja():
    try:
        rtemplate = Environment(loader=BaseLoader).from_string(
            request.form["template"])
    except jinja2.exceptions.TemplateSyntaxError as e:
        return jsonify({'status': 'Error', 'message': str(e)})

    yamlvalues = yaml.load(request.form["values"])
    if yamlvalues is None:
        yamlvalues = {}

    result = {'status': 'OK', 'message': rtemplate.render(
        **yamlvalues).replace("\n", "<br/>")}
    return jsonify(result)


def run():
    run_simple('127.0.0.1', 5000, app)
