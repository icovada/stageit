"""Main Flask APPlication."""
from time import sleep
import os
from uuid import uuid4 as uuid
import pickle
from werkzeug.serving import run_simple
from flask import Flask, request, stream_with_context, Response, render_template, jsonify
import yaml
from jinja2 import Environment, BaseLoader
import jinja2
from libs.db import Templates, History, Tasks, newsession
import config

APP_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(APP_PATH, 'web')

APP = Flask(__name__, template_folder=TEMPLATE_PATH)


class InvalidUsage(Exception):
    """Define method to return error. Taken from Flask docs."""

    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        """Init class."""
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        """Taken from docs."""
        ret_val = dict(self.payload or ())
        ret_val['message'] = self.message
        return ret_val


@APP.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    """Handle errors."""
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

# User Interface


@APP.route("/")
def home():
    """Render home page."""
    return render_template("templates/layout.html")


@APP.route("/workers")
def workers():
    """Render workers list."""
    text = render_template("templates/workers.html",
                           workers=config.WORKER_DICT)
    return text


@APP.route("/templates")
def templates():
    """Render template list."""
    session = newsession()
    dbtemplates = session.query(Templates.pkid,
                                Templates.name,
                                Templates.description)

    return render_template("templates/templates.html",
                           header=("Name", "Description"),
                           table=dbtemplates.all())


@APP.route("/tasks")
def tasks():
    """Render task list."""
    session = newsession()
    dbtasks = session.query(Tasks.pkid,
                            Tasks.fktemplate,
                            Tasks.description)

    return render_template("templates/tasks.html",
                           header=("ID", "Template", "Description"),
                           table=dbtasks.all(),
                           workers=config.WORKER_DICT.keys())


@APP.route("/history")
def history():
    """Render history list."""
    session = newsession()
    dbtasks = session.query(History.pkid,
                            History.serial_number,
                            History.model,
                            History.description)

    return render_template("templates/history.html",
                           table=dbtasks.all())


@APP.route("/templates/<templateid>")
def templatedetail(templateid):
    """Render template detail page."""
    session = newsession()
    template = session.query(Templates).get(templateid)
    templatedict = template.__dict__

    if template.templatevalues is not None:
        templatedict['templatevalues'] = yaml.dump(
            pickle.loads(template.templatevalues))
    else:
        templatedict['templatevalues'] = ''

    return render_template('templates/templates/detail.html', **templatedict)


@APP.route("/templates/add")
def templatesadd():
    """Render template addition page."""
    return render_template("templates/templates/add.html")


@APP.route("/tasks/add")
def createtask():
    """Render task addition page."""
    fktemplate = request.args.get('fktemplate')
    session = newsession()
    template = session.query(Templates).get(fktemplate)
    templatedict = template.__dict__

    if template.templatevalues is not None:
        templatedict['templatevalues'] = yaml.dump(
            pickle.loads(template.templatevalues))
    else:
        templatedict['templatevalues'] = ''

    return render_template("templates/tasks/add.html", fktemplate=fktemplate, **templatedict)


@APP.route("/tasks/<taskid>")
def taskdetail(taskid):
    """Render task detail page."""
    session = newsession()
    task = session.query(Tasks).get(taskid)
    taskdict = task.__dict__

    return render_template('templates/tasks/detail.html', **taskdict)


# API


@APP.route('/api/worker', methods={'POST'})
def enqueue():
    """Assign task to worker."""
    session = newsession()
    argdict = request.form.to_dict()

    # Check if task exists
    task = session.query(Tasks).get(argdict['taskpkid'])

    config.WORKER_DICT[argdict['worker']]['queue'].put(task.pkid)
    return "OK"


@APP.route("/api/templates", methods=['POST'])
def apiaddtemplate():
    """Add template API."""
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


@APP.route("/api/templates/<pkid>", methods=['PUT'])
def apiupdatetemplate(pkid):
    """Update template API."""
    session = newsession()

    template = session.query(Templates).get(pkid)
    # Check the template is not associated with pending tasks
    if not len:
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


@APP.route("/api/templates/<pkid>", methods=['DELETE'])
def apideletetemplate(pkid):
    """Delete template API."""
    session = newsession()
    template = session.query(Templates).get(pkid)
    session.delete(template)
    try:
        session.commit()
    except:
        raise InvalidUsage("Template used by one or more tasks", 412)

    return "OK"


@APP.route("/api/tasks", methods=['POST'])
def apiaddtask():
    """Add task API."""
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


@APP.route("/api/tasks/<pkid>", methods=['DELETE'])
def apideletetask(pkid):
    """Delete task API."""
    session = newsession()
    task = session.query(Tasks).get(pkid)
    session.delete(task)
    try:
        session.commit()
    except:
        raise InvalidUsage("Failed", 412)

    return "OK"


# Backend

@APP.route("/log/<worker>")
def log(worker):
    """Return stream of worker console log."""
    def streambytes():
        oldposition = 0
        while config.WORKER_DICT[worker]['thread'].status != "Waiting for work":
            sleep(0.1)
            newbuffer = config.WORKER_DICT[worker]['thread'].driver.getlog()
            yield newbuffer[oldposition:].replace("\n", "<br/>")
            oldbuffer = newbuffer
            oldposition = len(oldbuffer)

    try:
        if config.WORKER_DICT[worker]['thread'].status != "Waiting for work":
            return Response(stream_with_context(streambytes()))
        else:
            return "No work queued, come back later"
    except AttributeError:
        return "Discovering platform, please refresh later"


@APP.route("/jobstatus/<worker>")
def jobstatus(worker):
    """Return Worker.status."""
    print(config.WORKER_DICT)
    return config.WORKER_DICT[worker]['thread'].getstatus()


# AJAX

@APP.route("/api/convertjinja", methods=['POST'])
def convertjinja():
    """Return rendered Jinja2 template."""
    try:
        rtemplate = Environment(loader=BaseLoader).from_string(
            request.form["template"])
    except jinja2.exceptions.TemplateSyntaxError as exception:
        return jsonify({'status': 'Error', 'message': str(exception)})

    yamlvalues = yaml.load(request.form["values"])
    if yamlvalues is None:
        yamlvalues = {}

    result = {'status': 'OK', 'message': rtemplate.render(
        **yamlvalues).replace("\n", "<br/>")}
    return jsonify(result)


def run():
    """Run APP."""
    run_simple('127.0.0.1', 5000, APP)
