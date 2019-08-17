from django.views.generic import FormView, TemplateView
from django.urls import reverse_lazy

from .forms import TerminalServerForm

import stageitweb.stageit.models as models

class TerminalServerFormView(FormView):
    form_class = TerminalServerForm
    template_name = 'stageit/terminalserver_form.html'
