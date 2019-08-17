from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, Row, Column, Field

import stageitweb.stageit.models as models


def TerminalServerMapper():
    out = ()
    for row in models.TerminalServer.objects.all():
        out = ((row.pkid, row.name),) + out
    
    return out


class TerminalServerForm(forms.ModelForm):
    name = forms.CharField()
    model = forms.ChoiceField(choices=(('cisco','Cisco'),))
    hostname = forms.CharField()
    transport = forms.ChoiceField(choices=(('telnet', 'Telnet'), ('ssh', 'SSH')))
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta():
        model = models.TerminalServer
        fields = '__all__'


class SerialPortForm(forms.ModelForm):
    fkterminalserver = forms.ChoiceField(choices=TerminalServerMapper())
    transport = forms.ChoiceField(choices=(('telnet', 'Telnet'), ('ssh', 'SSH')))
    port = forms.IntegerField(min_value=1, max_value=65535)
    line = forms.IntegerField(min_value=1, max_value=65535)

    class Meta():
        model = models.SerialPort
        fields = '__all__'
