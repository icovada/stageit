from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from django.views.generic import FormView

from . import forms as forms
from . import settings as settings

import stageitweb.stageit.models as models
import pickle
import json

# Create your views here.
def index(request):
    return render(request, 'stageit/home.html')

def templates(request):
    return render(request, 'stageit/templates.html')

def templatesdetail(request, uuid):
    data = models.Template.objects.get(pkid=uuid).__dict__
    data['templatevalues'] = json.dumps(data['templatevalues'], indent=4, sort_keys=True)

    return render(request, 'stageit/templates/detail.html', data)

def templatesadd(request):
    return render(request, 'stageit/templates/add.html')

def history(request):
    return render(request, 'stageit/history.html')

def historydetail(request, uuid):
    instance = models.History.objects.get(pkid=uuid)
    data = {'instance': instance}
    return render(request, 'stageit/history/detail.html', data)

def historyadd(request, uuid):
    from stageit.libs.base_worker import baseworker as bw

    # Check there are no other running workers for this task
    if models.History.objects.filter(fktask = uuid, status = "In progress").count() > 0:
        return HttpResponseForbidden("A worker is already running for this task")
    
    if request.method == 'POST':
        form = forms.EnqueueTask(request.POST)
        if form.is_valid():
            history = models.History()
            history.fktask = uuid
            history.status = "Queued"
            history.fkserialport = "b3527269-53ca-483b-9e14-55617c1682f1"
            history.save()
            bw.delay(fkhistory=str(history.pkid), apipath=settings.API_BASE_URL)
            return redirect('/history/' + str(history.pkid))

    else:
        form = forms.EnqueueTask()

        return render(request, 'stageit/history/add.html', {'form': form, 'uuid': uuid})

def tasks(request):
    return render(request, 'stageit/tasks.html')

def tasksdetail(request, uuid):
    task = models.Task.objects.get(pkid=uuid)
    data = task.__dict__.copy()

    data['taskvalues'] = json.dumps(data['taskvalues'], indent=4, sort_keys=True)
    data['filepath'] = task.fktemplate.filepath
    data['installmode'] = task.fktemplate.installmode
    data['platform'] = task.fktemplate.platform
    data['poststaging'] = task.fktemplate.poststaging
    data['template'] = task.fktemplate.template
    data['name'] = task.fktemplate.name

    return render(request, 'stageit/tasks/detail.html', data)

def tasksadd(request, uuid):
    data = models.Template.objects.get(pkid=uuid).__dict__
    data['templatevalues'] = json.dumps(data['templatevalues'], indent=4, sort_keys=True)
    data['fktemplate'] = str(uuid)
    data['slug'] = str(uuid)[:5]
    return render(request, 'stageit/tasks/add.html', data)



def sandbox(request):
    return render(request, 'stageit/jinja_sandbox.html')