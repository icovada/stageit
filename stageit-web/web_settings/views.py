import os
import yaml

from django.conf import settings
from django.core.files.storage import default_storage
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import (CreateView, DeleteView, FormView,
                                  UpdateView)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator



import web_interface.models as models

from .forms import (SerialPortForm, TerminalServerForm,
                    UploadFileForm, RemoteWorkerForm)

baseform = 'stageit/baseform.html'

@login_required
def terminalserver(request):
    data = {'settingsmenu': True,
            'pagename': 'terminalserver'}
    return render(request, 'stageit/terminalserver_list.html', data)


class TerminalServerCreate(LoginRequiredMixin, CreateView):
    form_class = TerminalServerForm
    model = models.TerminalServer
    template_name = baseform


class TerminalServerUpdate(LoginRequiredMixin, UpdateView):
    form_class = TerminalServerForm
    model = models.TerminalServer
    template_name = baseform


class TerminalServerDelete(LoginRequiredMixin, DeleteView):
    form_class = TerminalServerForm
    model = models.TerminalServer
    template_name = baseform


@login_required
def serialport(request):
    data = {'settingsmenu': True,
            'pagename': 'serialport'}
    return render(request, 'stageit/serialport_list.html', data)


class SerialPortCreate(LoginRequiredMixin, CreateView):
    form_class = SerialPortForm
    model = models.SerialPort
    template_name = baseform


class SerialPortUpdate(LoginRequiredMixin, UpdateView):
    form_class = SerialPortForm
    model = models.SerialPort
    template_name = baseform


class SerialPortDelete(LoginRequiredMixin, DeleteView):
    form_class = SerialPortForm
    model = models.SerialPort
    template_name = baseform


@login_required
def remoteworker(request):
    data = {'settingsmenu': True,
            'pagename': 'remoteworker'}
    return render(request, 'stageit/remoteworker_list.html', data)

class RemoteWorkerCreate(LoginRequiredMixin, CreateView):
    form_class = RemoteWorkerForm
    model = models.RemoteWorker
    template_name = baseform

class RemoteWorkerUpdate(LoginRequiredMixin, UpdateView):
    form_class = RemoteWorkerForm
    model = models.RemoteWorker
    template_name = baseform

class RemoteWorkerDelete(LoginRequiredMixin, DeleteView):
    form_class = RemoteWorkerForm
    model = models.RemoteWorker
    template_name = baseform

@login_required
def filemanager(request):
    return render(request, 'stageit/filemanager.html')


@login_required
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            fileobject = request.FILES['file']
            filename = fileobject.name
            save_path = os.path.join(settings.MEDIA_ROOT, filename)
            default_storage.save(save_path, fileobject)
            models.Firmware.objects.create(filename=filename)
            return HttpResponseRedirect('/settings/filemanager/')
    else:
        form = UploadFileForm()
    return render(request, 'stageit/upload.html', {'form': form})


@login_required
def bootstrapconfig(request):
    data = {'settingsmenu': True,
            'pagename': 'bootstrapconfig'}
    return render(request, 'stageit/bootstrapconfig_list.html', data)


@login_required
def bootstrapconfigadd(request):
    data = {'settingsmenu': True,
            'pagename': 'bootstrapconfig'}
    return render(request, 'stageit/bootstrapconfig/add.html', data)


@login_required
def bootstrapconfigdetail(request, uuid):
    data = models.BootstrapConfig.objects.get(pkid=uuid).__dict__
    data['values'] = yaml.dump(data['values'], indent=4, sort_keys=True)
    data['settingsmenu'] = True
    data['pagename'] = 'bootstrapconfig'
    return render(request, 'stageit/bootstrapconfig/detail.html', data)
