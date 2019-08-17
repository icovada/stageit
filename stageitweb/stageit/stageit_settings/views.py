from django.views.generic import FormView, TemplateView
from django.urls import reverse_lazy

from .forms import TerminalServerForm, SerialPortForm

import stageitweb.stageit.models as models

class TerminalServerFormView(FormView):
    form_class = TerminalServerForm
    template_name = 'stageit/terminalserver_add.html'

class SerialPortFormView(FormView):
    form_class = SerialPortForm
    template_name = 'stageit/serialport_add.html'