from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import django_filters.rest_framework
from rest_framework.parsers import JSONParser
from rest_framework import viewsets, filters
import web_interface.models as models
import api.serializers as serializers
from rest_framework import generics

import glob
import json
from jinja2 import Environment, BaseLoader
import jinja2


class TemplateViewSet(viewsets.ModelViewSet):
    queryset = models.Template.objects.all()
    serializer_class = serializers.TemplateSerializer 

class TaskViewSet(viewsets.ModelViewSet):
    queryset = models.Task.objects.all()
    serializer_class = serializers.TaskSerializer
    
class HistoryViewSet(viewsets.ModelViewSet):
    queryset = models.History.objects.all()
    serializer_class = serializers.HistorySerializer
    filter_backends = [filters.OrderingFilter]
    ordering = ['status']

class LogViewSet(viewsets.ModelViewSet):
    queryset = models.Log.objects.all()
    serializer_class = serializers.LogSerializer
    # https://stackoverflow.com/questions/57479402/choosing-column-to-search-by-in-django-rest-framework
    lookup_field = 'fkhistory'
    lookup_url_kwarg = 'fkhistory'
    filter_fields = {
        'sequence': ['gte', 'lte'],
        'fkhistory': ['exact']
    }

class RemoteWorkerViewSet(viewsets.ModelViewSet):
    queryset = models.RemoteWorker.objects.all()
    serializer_class = serializers.RemoteWorkerSerializer

class TerminalServerViewSet(viewsets.ModelViewSet):
    queryset = models.TerminalServer.objects.all()
    serializer_class = serializers.TerminalServerSerializer


class SerialPortViewSet(viewsets.ModelViewSet):
    queryset = models.SerialPort.objects.all()
    serializer_class = serializers.SerialPortSerializer
    filter_fields = {
        'fkterminalserver' : ['exact']
    }

class BootstrapConfigSet(viewsets.ModelViewSet):
    queryset = models.BootstrapConfig.objects.all()
    serializer_class = serializers.BootstrapConfigSerializer

@csrf_exempt
def convertjinja(request):
    """Return rendered Jinja2 template."""
    try:
        rtemplate = Environment(loader=BaseLoader).from_string(request.POST['template'])
    except jinja2.exceptions.TemplateSyntaxError as exception:
        return HttpResponse(str(exception), status=500)

    yamlvalues = json.loads(request.POST['values'])
    if yamlvalues is None:
        yamlvalues = {}

    result = rtemplate.render(**yamlvalues).replace("\n", "<br/>")
    return HttpResponse(result)


def loggenerator(uuid):
    """
    Yield all the logs from a fkhistory
    """
    from time import sleep
    logs = models.Log.objects.filter(fkhistory=uuid)
    lastlog = 0
    for log in logs:
        lastlog = log.sequence
        # Return newline before every new line because newlines
        # are stripped by djangorestframework
        # TODO: Fix this
        yield("\n")
        yield(log.log)

    history_row = models.History.objects.get(pkid=uuid)
    while history_row.status in ("In Progress", "Discovering"):
        logs = models.Log.objects.filter(fkhistory=uuid, sequence__gt=lastlog).order_by("sequence")
        for log in logs:
            lastlog = log.sequence
            # Return newline before every new line because newlines
            # are stripped by djangorestframework
            # TODO: Fix this
            yield("\n")
            yield(log.log)
        sleep(1)
        history_row.refresh_from_db()


def streamlogs(request, uuid):
    return StreamingHttpResponse(loggenerator(uuid))

def filemanager_list(request):
    filelist = []
    for f in glob.glob(settings.MEDIA_ROOT + '/*'):
        filelist.append({'name': f[len(settings.MEDIA_ROOT)+1:]})
    return JsonResponse(filelist, safe=False)