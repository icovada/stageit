from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework import viewsets
from stageitweb.stageit.models import Templates
from stageitweb.api.serializers import TemplatesSerializer

class TemplatesViewSet(viewsets.ModelViewSet):
    queryset = Templates.objects.all()
    serializer_class = TemplatesSerializer


@csrf_exempt
def templates_list(request):
    if request.method == 'GET':
        templates = Templates.objects.all()
        serializer = TemplatesSerializer(templates, many=True)
        return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def templates_detail(request, uuid):
    try:
        template = Templates.object.get(pkid=uuid)
    except Templates.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = TemplatesSerializer(template)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = TemplatesSerializer(template, data=data)
        if template.is_valid():
            template.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        template.delete()
        return HttpResponse(status=204)
