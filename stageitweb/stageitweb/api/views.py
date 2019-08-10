from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework import viewsets
from stageitweb.stageit.models import Templates, Tasks, History
from stageitweb.api.serializers import TemplatesSerializer, TasksSerializer, HistorySerializer

import yaml
from jinja2 import Environment, BaseLoader
import jinja2


class TemplatesViewSet(viewsets.ModelViewSet):
    queryset = Templates.objects.all()
    serializer_class = TemplatesSerializer 

class TasksViewSet(viewsets.ModelViewSet):
    queryset = Tasks.objects.all()
    serializer_class = TasksSerializer
    
class HistoryViewSet(viewsets.ModelViewSet):
    queryset = History.objects.all()
    serializer_class = HistorySerializer

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
