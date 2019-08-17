from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, Row, Column, Field

import stageitweb.stageit.models as models


class TerminalServerForm(forms.ModelForm):
    name = forms.CharField()
    model = forms.ChoiceField(choices=(('cisco','Cisco'),))
    hostname = forms.CharField()
    transport = forms.ChoiceField(choices=(('telnet', 'Telnet'), ('ssh', 'SSH')))
    username = forms.CharField()
    password = forms.PasswordInput()

    class Meta():
        model = models.TerminalServer
        fields = '__all__'
