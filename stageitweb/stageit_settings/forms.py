from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, Row, Column, Field

import stageitweb.stageit.models as models
from django.db.utils import OperationalError


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
    fkterminalserver = forms.ModelChoiceField(queryset=models.TerminalServer.objects)
    transport = forms.ChoiceField(choices=(('telnet', 'Telnet'), ('ssh', 'SSH')))
    port = forms.IntegerField(min_value=1, max_value=65535)
    line = forms.IntegerField(min_value=1, max_value=65535)

    class Meta():
        model = models.SerialPort
        fields = '__all__'


class UploadFileForm(forms.Form):
    file = forms.FileField()

    helper = FormHelper()
    helper.add_input(Submit('submit', 'Submit', css_class='btn-primary'))
    helper.form_method = 'POST'