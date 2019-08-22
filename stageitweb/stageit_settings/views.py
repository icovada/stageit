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


class TerminalServerFormView(FormView):
    form_class = TerminalServerForm
    template_name = 'stageit/terminalserver_add.html'

def terminalserver(request):
    return render(request, 'stageit/terminalserver_list.html')

def edit_terminal_server(request, uuid):
    instance = get_object_or_404(models.TerminalServer, pkid=uuid)
    form = TerminalServerForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect('next_view')
    return render(request, 'stageit/terminalserver_edit.html', {'form': form})


class SerialPortFormView(FormView):
    form_class = SerialPortForm
    template_name = 'stageit/serialport_add.html'

def serialport(request):
    return render(request, 'stageit/serialport_list.html')

def edit_serial_port(request, uuid):
    instance = get_object_or_404(models.SerialPort, pkid=uuid)
    form = SerialPortForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect('next_view')
    return render(request, 'stageit/serialport_edit.html', {'form': form})

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

class BootstrapConfigUpdate(UpdateView):
    form_class = BootstrapConfigForm
    model = models.BootstrapConfig

class BootstrapConfigDelete(DeleteView):
    form_class = BootstrapConfigForm
    model = models.BootstrapConfig
    success_url = "/settings/bootstrapconfig"


