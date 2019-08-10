from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework import viewsets
from stageitweb.stageit.models import Templates, Tasks, History
from stageitweb.api.serializers import TemplatesSerializer, TasksSerializer, HistorySerializer

class TemplatesViewSet(viewsets.ModelViewSet):
    queryset = Templates.objects.all()
    serializer_class = TemplatesSerializer 

class TasksViewSet(viewsets.ModelViewSet):
    queryset = Tasks.objects.all()
    serializer_class = TasksSerializer
    
class HistoryViewSet(viewsets.ModelViewSet):
    queryset = History.objects.all()
    serializer_class = HistorySerializer
        
            

# @csrf_exempt
# def templates_list(request):
#     if request.method == 'GET':
#         templates = Templates.objects.all()
#         serializer = TemplatesSerializer(templates, many=True)
#         return JsonResponse(serializer.data, safe=False)

# @csrf_exempt
# def tasks_list(request):
#     if request.method == 'GET':
#         tasks = Tasks.objects.all()
#         serializer = TasksSerializer(tasks, many=True)
#         return JsonResponse(serializer.data, safe=False)

# @csrf_exempt
# def history_list(request):
#     if request.method == 'GET':
#         history = History.objects.all()
#         serializer = HistorySerializer(history, many=True)
#         return JsonResponse(serializer.data, safe=False)

# @csrf_exempt
# def templates_detail(request, uuid):
#     try:
#         template = Templates.object.get(pkid=uuid)
#     except Templates.DoesNotExist:
#         return HttpResponse(status=404)

#     if request.method == 'GET':
#         serializer = TemplatesSerializer(template)
#         return JsonResponse(serializer.data)

#     elif request.method == 'PUT':
#         data = JSONParser().parse(request)
#         serializer = TemplatesSerializer(template, data=data)
#         if template.is_valid():
#             template.save()
#             return JsonResponse(serializer.data)
#         return JsonResponse(serializer.errors, status=400)

#     elif request.method == 'DELETE':
#         template.delete()
#         return HttpResponse(status=204)

# @csrf_exempt
# def tasks_detail(request, uuid):
#     try:
#         task = Tasks.object.get(pkid=uuid)
#     except Tasks.DoesNotExist:
#         return HttpResponse(status=404)

#     if request.method == 'GET':
#         serializer = TasksSerializer(task)
#         return JsonResponse(serializer.data)

#     elif request.method == 'PUT':
#         data = JSONParser().parse(request)
#         serializer = TasksSerializer(task, data=data)
#         if task.is_valid():
#             task.save()
#             return JsonResponse(serializer.data)
#         return JsonResponse(serializer.errors, status=400)

#     elif request.method == 'DELETE':
#         task.delete()
#         return HttpResponse(status=204)

# @csrf_exempt
# def history_detail(request, uuid):
#     try:
#         history = History.object.get(pkid=uuid)
#     except History.DoesNotExist:
#         return HttpResponse(status=404)

#     if request.method == 'GET':
#         serializer = HistorySerializer(task)
#         return JsonResponse(serializer.data)

#     elif request.method == 'PUT':
#         data = JSONParser().parse(request)
#         serializer = HistorySerializer(task, data=data)
#         if history.is_valid():
#             history.save()
#             return JsonResponse(serializer.data)
#         return JsonResponse(serializer.errors, status=400)

#     elif request.method == 'DELETE':
#         history.delete()
#         return HttpResponse(status=204)