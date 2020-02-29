import json
import yaml

from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

import web_interface.models as models

from . import forms as forms


# Create your views here.
@login_required
def index(request):
    return render(request, 'stageit/home.html')


@login_required
def templates(request):
    return render(request, 'stageit/templates.html')


@login_required
def templatesdetail(request, uuid):
    template = models.Template.objects.get(pkid=uuid)
    templatedict = template
    templatedict.templatevalues = yaml.dump(
        template.templatevalues, indent=4, sort_keys=True)
    bootstrapconfig = models.BootstrapConfig.objects.all()
    data = {'template': templatedict,
            'bootstrapconfig': bootstrapconfig}

    return render(request, 'stageit/templates/detail.html', data)


@login_required
def templatesadd(request):
    bootstrapconfig = models.BootstrapConfig.objects.all()
    data = {'bootstrapconfig': bootstrapconfig}
    return render(request, 'stageit/templates/add.html', data)


@login_required
def history(request):
    return render(request, 'stageit/history.html')


@login_required
def historydetail(request, uuid):
    bootstrapconfig = models.BootstrapConfig.objects.all()
    instance = models.History.objects.get(pkid=uuid)
    data = {'instance': instance,
            'bootstrapconfig': bootstrapconfig}
    return render(request, 'stageit/history/detail.html', data)


@login_required
def historyadd(request, uuid):
    # Check there are no other running workers for this task
    if models.History.objects.filter(fktask=uuid, status="In Progress").count() > 0:
        return HttpResponseForbidden("A worker is already running for this task")

    if request.method == 'POST':
        form = forms.EnqueueTask(request.POST)
        if form.is_valid():
            history = models.History()
            history.fktask = uuid
            history.status = "Queued"
            history.fkserialport = request.POST.get('fkserialport')
            history.fkremoteworker = history.fkserialport.fkterminalserver.fkremoteworker
            history.save()
            return redirect('/history/' + str(history.pkid))

    else:
        form = forms.EnqueueTask()

        return render(request, 'stageit/history/add.html', {'form': form, 'uuid': uuid})


@login_required
def tasks(request):
    return render(request, 'stageit/tasks.html')


@login_required
def tasksdetail(request, uuid):
    task = models.Task.objects.get(pkid=uuid)
    data = task.__dict__.copy()

    data['taskvalues'] = yaml.dump(
        data['taskvalues'], indent=4, sort_keys=True)
    data['filepath'] = task.fktemplate.filepath
    data['installmode'] = task.fktemplate.installmode
    data['poststaging'] = task.fktemplate.poststaging
    data['template'] = task.fktemplate.template
    data['name'] = task.fktemplate.name

    data['taskbusy'] = models.History.objects.filter(fktask=uuid, status="In Progress").count() > 0

    return render(request, 'stageit/tasks/detail.html', data)


@login_required
def tasksadd(request, uuid):
    data = models.Template.objects.get(pkid=uuid).__dict__
    data['templatevalues'] = yaml.dump(
        data['templatevalues'], indent=4, sort_keys=True)
    data['fktemplate'] = str(uuid)
    data['slug'] = str(uuid)[:5]
    return render(request, 'stageit/tasks/add.html', data)


@login_required
def sandbox(request):
    return render(request, 'stageit/jinja_sandbox.html')

def login(request):
    return render(request, 'stageit/login.html')