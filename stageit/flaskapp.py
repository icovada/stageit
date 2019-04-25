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
import libs.db as db
import pickle
from sqlalchemy.sql.expression import select, insert

APP_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(APP_PATH, 'stageit/web/templates')

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


@app.route("/")
def home():
    return render_template("layout.html")


@app.route("/workers")
def workers():
    text = render_template("workers.html", workers=config.worker_array)
    return text


@app.route("/templates")
def tasks():
    templatecolumns = db.templates.columns
    query = select((templatecolumns['id'],
                    templatecolumns['name'],
                    templatecolumns['description']))
    res = db.conn.execute(query)
    allrows = res.fetchall()

    return render_template("templates.html", header=("Name", "Description"), table=allrows)


@app.route("/templates/<templateid>/add", methods=['POST'])
def templatemanager(templateid):
    templatecolumns = db.templates.columns
    query = select(templatecolumns).where(templatecolumns['id'] == templateid)
    res = db.conn.execute(query)
    dbdata = res.fetchone()
    if dbdata is None:
        raise InvalidUsage("Template ID not valid", 500)

    query = insert(db.tasks).values(id=str(uuid()),
                                    fktemplate=dbdata['id'],
                                    taskvalues=pickle.dumps(yaml.load(request.form['taskvalues'])))
    res=db.conn.execute(query)
    redirect(url_for('/tasks/' + templateid))


@app.route("/templates/<templateid>/create")
def createtemplate(templateid):
    templatecolumns=db.templates.columns
    query=select(templatecolumns).where(templatecolumns['id'] == templateid)
    res=db.conn.execute(query)
    dbdata=res.fetchone()
    if dbdata is None:
        raise InvalidUsage("Template ID not valid", 500)

    templatedict=dict(zip(dbdata.keys(), dbdata.values()))
    templatedict['templatevalues']=yaml.dump(
        pickle.loads(templatedict['templatevalues']))

    return render_template("templates/createtask.html", uuid=templateid, **templatedict)

@app.route("/tasks/<taskid>")
def taskdetail(taskid):
    return render_template("tasks/taskdetail.html")


@app.route("/templates/add")
def templates():
    return render_template("templates/add.html")


@app.route("/modal")
def modal():
    return render_template("test/modal.html")


@app.route("/api/addtemplate", methods=['POST'])
def apiaddtemplate():
    argdict=request.form.copy()
    argdict['id']=str(uuid())
    del argdict['templatevalues']
    argdict['templatevalues']=pickle.dumps(
        yaml.load(request.form['templatevalues']))
    print("VARS")
    print(argdict)
    ins=db.templates.insert().values(id=argdict['id'],
                                       name=argdict['name'],
                                       description=argdict['description'],
                                       platform=argdict['platform'],
                                       template=argdict['template'],
                                       templatevalues=argdict['templatevalues'],
                                       filepath=argdict['filepath'],
                                       poststaging=argdict['poststaging'])
    db.conn.execute(ins)
    return argdict['id']


@app.route("/api/addtask", methods=['POST'])
def apiaddtask():
    argdict=request.form.copy()
    argdict['id']=str(uuid())
    del argdict['templatevalues']
    argdict['templatevalues']=pickle.dumps(
        yaml.load(request.form['templatevalues']))
    print("VARS")
    print(argdict)
    ins=db.templates.insert().values(**argdict)
    db.conn.execute(ins)
    return argdict['id']


@app.route("/api/convertjinja", methods=['POST'])
def convertjinja():
    try:
        rtemplate=Environment(loader=BaseLoader).from_string(
            request.form["template"])
    except jinja2.exceptions.TemplateSyntaxError as e:
        return jsonify({'status': 'Error', 'message': str(e)})

    yamlvalues=yaml.load(request.form["values"])
    if yamlvalues is None:
        yamlvalues={}

    result={'status': 'OK', 'message': rtemplate.render(
        **yamlvalues).replace("\n", "<br/>")}
    return jsonify(result)


@app.route("/log/<worker>")
def log(worker):
    def streambytes():
        oldposition=0
        while config.worker_array[worker]['thread'].status != "Waiting for work":
            sleep(0.1)
            newbuffer=config.worker_array[worker]['thread'].driver.getlog()
            yield newbuffer[oldposition:].replace("\n", "<br/>")
            oldbuffer=newbuffer
            oldposition=len(oldbuffer)

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
    queueme=request.form.copy()
    queueme['tempconfig']=json.loads(request.form['tempconfig'])
    queueme['finalconfig']=json.loads(request.form['finalconfig'])
    config.worker_array[worker]['queue'].put(queueme)
    return "OK"


def run():
    run_simple('127.0.0.1', 5000, app)
