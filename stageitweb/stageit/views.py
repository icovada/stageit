from django.shortcuts import render

from stageitweb.stageit.models import Templates, Tasks, History
import pickle
import json

# Create your views here.
def index(request):
    return render(request, 'stageit/home.html')

def templates(request):
    return render(request, 'stageit/templates.html')

def templatesdetail(request, uuid):
    data = Templates.objects.get(pkid=uuid).__dict__
    data['templatevalues'] = json.dumps(data['templatevalues'], indent=4, sort_keys=True)

    return render(request, 'stageit/templates/detail.html', data)

def templatesadd(request):
    return render(request, 'stageit/templates/add.html')

def history(request):
    return render(request, 'stageit/history.html')

def historydetail(request, uuid):
    return render(request, 'stageit/history/detail.html')

def historyadd(request, uuid):
    from uuid import uuid4
    from stageit.libs.fake_worker import fakeworker as fw
    history = History()
    history.pkid = uuid4()
    history.fktask = uuid
    history.save()

    fw.delay(fkhistory=str(history.pkid))

    return render(request, 'stageit/history/add.html')

def tasks(request):
    return render(request, 'stageit/tasks.html')

def tasksdetail(request, uuid):
    task = Tasks.objects.get(pkid=uuid)
    data = Tasks.objects.get(pkid=uuid).__dict__.copy()

    data['taskvalues'] = json.dumps(data['taskvalues'], indent=4, sort_keys=True)
    data['filepath'] = task.fktemplate.filepath
    data['installmode'] = task.fktemplate.installmode
    data['platform'] = task.fktemplate.platform
    data['poststaging'] = task.fktemplate.poststaging
    data['template'] = task.fktemplate.template
    data['name'] = task.fktemplate.name

    return render(request, 'stageit/tasks/detail.html', data)

def tasksadd(request, uuid):
    data = Templates.objects.get(pkid=uuid).__dict__
    data['templatevalues'] = json.dumps(data['templatevalues'], indent=4, sort_keys=True)
    data['fktemplate'] = str(uuid)
    data['slug'] = str(uuid)[:5]
    return render(request, 'stageit/tasks/add.html', data)