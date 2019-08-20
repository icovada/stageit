from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, Row, Column, Field

import stageitweb.stageit.models as models
from django.db.utils import OperationalError


class EnqueueTask(forms.Form):
    fkserialport = forms.ModelChoiceField(queryset=models.SerialPort.objects)

    helper = FormHelper()
    helper.add_input(Submit('submit', 'Submit', css_class='btn-primary'))
    helper.form_method = 'POST'