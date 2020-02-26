import ast

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Div, Layout, Submit, Button
from django import forms

import web_interface.models as models


separator = """<hr class="mb-4">"""

class TerminalServerForm(forms.ModelForm):
    name = forms.CharField()
    model = forms.ChoiceField(choices=(('cisco', 'Cisco'),))
    fkremoteworker = forms.ModelChoiceField(
        queryset=models.RemoteWorker.objects, label="Remote Worker that will process tasks on this Terminal Server")
    hostname = forms.CharField()
    transport = forms.ChoiceField(
        choices=(('telnet', 'Telnet'), ('ssh', 'SSH')))
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    helper = FormHelper()
    helper.add_input(Submit('submit', 'Submit', css_class='btn btn-primary btn-lg btn-block'))
    helper.form_method = 'POST'

    class Meta:
        model = models.TerminalServer
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super(TerminalServerForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class SerialPortForm(forms.ModelForm):
    fkterminalserver = forms.ModelChoiceField(
        queryset=models.TerminalServer.objects, label="Terminal Server")
    transport = forms.ChoiceField(choices=(('telnet', 'Telnet'), ('ssh', 'SSH')),
                                  help_text="SSH not supported for Serial over IP connections")
    port = forms.IntegerField(min_value=1, max_value=65535)
    line = forms.IntegerField(min_value=1, max_value=65535)

    helper = FormHelper()
    helper.add_input(Submit('submit', 'Submit', css_class='btn-primary'))
    helper.form_method = 'POST'

    class Meta:
        model = models.SerialPort
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(SerialPortForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class RemoteWorkerForm(forms.ModelForm):
    name = forms.CharField()
    # TODO: disable field and auto generate token
    token = forms.CharField()

    helper = FormHelper()
    helper.add_input(Submit('submit', 'Submit', css_class='btn-primary'))
    helper.form_method = 'POST'

    class Meta:
        model = models.RemoteWorker
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(RemoteWorkerForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class UploadFileForm(forms.Form):
    file = forms.FileField()

    helper = FormHelper()
    helper.add_input(Submit('submit', 'Submit', css_class='btn-primary'))
    helper.form_method = 'POST'
