import os

from django.core.files.storage import default_storage
from django.views.generic import FormView, TemplateView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.conf import settings

from .forms import TerminalServerForm, SerialPortForm, UploadFileForm, BootstrapConfigForm

import stageitweb.stageit.models as models
import json

baseform = 'stageit/baseform.html'

def terminalserver(request):
    return render(request, 'stageit/terminalserver_list.html')

class TerminalServerCreate(CreateView):
    form_class = TerminalServerForm
    model = models.TerminalServer
    template_name = baseform

class TerminalServerUpdate(UpdateView):
    form_class = TerminalServerForm
    model = models.TerminalServer
    template_name = baseform

class TerminalServerDelete(DeleteView):
    form_class = TerminalServerForm
    model = models.TerminalServer()
    template_name = baseform


def serialport(request):
    return render(request, 'stageit/serialport_list.html')

class SerialPortCreate(CreateView):
    form_class = SerialPortForm
    model = models.SerialPort
    template_name = baseform

class SerialPortUpdate(UpdateView):
    form_class = SerialPortForm
    model = models.SerialPort
    template_name = baseform

class SerialPortDelete(DeleteView):
    form_class = SerialPortForm
    model = models.SerialPort
    template_name = baseform


def filemanager(request):
    return render(request, 'stageit/filemanager.html')

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


def bootstrapconfig(request):
    return render(request, 'stageit/bootstrapconfig_list.html')


class BootstrapConfigCreate(CreateView):
    form_class = BootstrapConfigForm
    model = models.BootstrapConfig
    template_name = baseform
    success_url = "/settings/bootstrapconfig"

class BootstrapConfigUpdate(UpdateView):
    form_class = BootstrapConfigForm
    model = models.BootstrapConfig
    template_name = baseform
    success_url = "/settings/bootstrapconfig"

class BootstrapConfigDelete(DeleteView):
    form_class = BootstrapConfigForm
    model = models.BootstrapConfig
    template_name = baseform
    success_url = "/settings/bootstrapconfig"


