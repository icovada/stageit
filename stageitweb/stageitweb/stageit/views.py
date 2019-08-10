from django.shortcuts import render

from stageitweb.stageit.models import Templates, Tasks, History
import pickle

# Create your views here.
def index(request):
    return render(request, 'stageit/home.html')

def templates(request):
    return render(request, 'stageit/templates.html')

def templatesdetail(request, uuid):
    data = Templates.objects.get(pkid=uuid).__dict__
    data['templatevalues'] = pickle.loads(data['templatevalues'])

    return render(request, 'stageit/templates/detail.html', data)

def templatesadd(request):
    return render(request, 'stageit/templates/add.html')

def history(request):
    return render(request, 'stageit/history.html')

def historydetail(request, uuid):
    return render(request, 'stageit/history/detail.html')

def tasks(request):
    return render(request, 'stageit/tasks.html')

def tasksdetail(request, uuid):
    return render(request, 'stageit/tasks/detail.html')