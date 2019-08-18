from django.views.generic import FormView, TemplateView
from django.urls import reverse_lazy

from .forms import TerminalServerForm, SerialPortForm

import stageitweb.stageit.models as models

from django.shortcuts import get_object_or_404, redirect, render


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
