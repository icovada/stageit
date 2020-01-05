from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, Row, Column, Field, Button, HTML
from crispy_forms.bootstrap import FormActions

import stageitweb.stageit.models as models
from django.db.utils import OperationalError

import ast

separator = """<hr class="mb-4">"""

class TerminalServerForm(forms.ModelForm):
    name = forms.CharField()
    model = forms.ChoiceField(choices=(('cisco', 'Cisco'),))
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


class UploadFileForm(forms.Form):
    file = forms.FileField()

    helper = FormHelper()
    helper.add_input(Submit('submit', 'Submit', css_class='btn-primary'))
    helper.form_method = 'POST'


class BootstrapConfigForm(forms.ModelForm):
    name = forms.CharField()
    description = forms.CharField()
    bootstraptemplate = forms.CharField(widget=forms.Textarea(), label="Boostrap Config Template")
    values = forms.CharField(widget=forms.Textarea())

    def clean_values(self):
        jdata = self.cleaned_data['values']
        try:
            json_data = ast.literal_eval(jdata)
        except Exception as e:
            raise forms.ValidationError(e)

        return json_data

    class Meta:
        model = models.BootstrapConfig
        fields = '__all__'
        
    helper = FormHelper()
    helper.layout = Layout(
        Div('name', css_class="form-row"),
        Div('description', css_class="form-row"),
        Column('bootstraptemplate', css_class="col-xl-6 form-left"),
        Column('values', css_class="col-xl-6 form-right"),
        Div(
            Submit('save', 'Save changes'),
        )
    )
    helper.form_method = 'POST'

