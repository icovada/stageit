from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
import django_filters.rest_framework
from rest_framework.parsers import JSONParser
from rest_framework import viewsets
import stageitweb.stageit.models as models
import stageitweb.api.serializers as serializers
from rest_framework import generics


import yaml
from jinja2 import Environment, BaseLoader
import jinja2


class TemplatesViewSet(viewsets.ModelViewSet):
    queryset = models.Templates.objects.all()
    serializer_class = serializers.TemplatesSerializer 

class TasksViewSet(viewsets.ModelViewSet):
    queryset = models.Tasks.objects.all()
    serializer_class = serializers.TasksSerializer
    
class HistoryViewSet(viewsets.ModelViewSet):
    queryset = models.History.objects.all()
    serializer_class = serializers.HistorySerializer

class LogViewSet(viewsets.ModelViewSet):
    queryset = models.Log.objects.all()
    serializer_class = serializers.LogSerializer
    filter_fields = {
        'sequence': ['gte', 'lte'],
        'fkhistory': ['exact']
    }

class TerminalServerViewSet(viewsets.ModelViewSet):
    queryset = models.TerminalServer.objects.all()
    serializer_class = serializers.TerminalServerSerializer


class SerialPortViewSet(viewsets.ModelViewSet):
    queryset = models.SerialPort.objects.all()
    serializer_class = serializers.SerialPortSerializer
    filter_fields = {
        'fkterminalserver' : ['exact']
    }


@csrf_exempt
def convertjinja(request):
    """Return rendered Jinja2 template."""
    try:
        rtemplate = Environment(loader=BaseLoader).from_string(request.POST['template'])
    except jinja2.exceptions.TemplateSyntaxError as exception:
        return JsonResponse({'status': 'Error', 'message': str(exception)})

    yamlvalues = yaml.load(request.POST['values'], Loader=yaml.FullLoader)
    if yamlvalues is None:
        yamlvalues = {}

    result = {'status': 'OK', 'message': rtemplate.render(
        **yamlvalues).replace("\n", "<br/>")}
    return JsonResponse(result)


def loggenerator(uuid):
    from time import sleep
    logs = models.Log.objects.filter(fkhistory=uuid)
    for log in logs:
        text = log.log
        text = text.replace("\n", "<br/>")
        sleep(1)
        yield(text)

def streamlogs(request, uuid):
    return StreamingHttpResponse(loggenerator(uuid))