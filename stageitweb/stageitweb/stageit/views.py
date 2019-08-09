from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'stageit/home.html')

def templates(request):
    return render(request, 'stageit/templates.html')

def templatesdetail(request, uuid):
    return render(request, 'stageit/templates/detail.html')

def history(request):
    return render(request, 'stageit/history.html')

def historydetail(request, uuid):
    return render(request, 'stageit/history/detail.html')

def tasks(request):
    return render(request, 'stageit/tasks.html')

def tasksdetail(request, uuid):
    return render(request, 'stageit/tasks/detail.html')