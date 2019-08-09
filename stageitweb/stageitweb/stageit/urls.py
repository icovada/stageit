from django.urls import path

from . import views

urlpatterns = [
    path('templates', views.templates, name='templates'),
    path('history', views.history, name='history'),
    path('tasks', views.tasks, name='tasks'),
    path('', views.index, name='index'),
]
