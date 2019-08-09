from django.urls import path

from . import views

urlpatterns = [
    path('templates', views.templates, name='templates'),
    path('templates/<uuid:uuid>', views.templatesdetail, name='templatesdetail'),
    path('history', views.history, name='history'),
    path('history/<uuid:uuid>', views.historydetail, name='historydetail'),
    path('tasks', views.tasks, name='tasks'),
    path('tasks/<uuid:uuid>', views.tasksdetail, name='tasksdetail'),
    path('', views.index, name='index'),
]
