from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return render(request, 'stageit/home.html')

def templates(request):
    return render(request, 'stageit/templates.html')

def history(request):
    return render(request, 'stageit/history.html')

def tasks(request):
    return render(request, 'stageit/tasks.html')