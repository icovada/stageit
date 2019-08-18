from django.urls import path, include

from . import views

urlpatterns = [
    path('templates', views.templates, name='templates'),
    path('templates/<uuid:uuid>', views.templatesdetail, name='templatesdetail'),
    path('templates/add', views.templatesadd, name='templatesadd'),
    path('history', views.history, name='history'),
    path('history/<uuid:uuid>', views.historydetail, name='historydetail'),
    path('history/new/<uuid:uuid>', views.historyadd, name='historyadd'),
    path('tasks', views.tasks, name='tasks'),
    path('tasks/<uuid:uuid>', views.tasksdetail, name='tasksdetail'),
    path('tasks/new/<uuid:uuid>', views.tasksadd, name='tasksadd'),
    path('settings/', include('stageitweb.stageit_settings.urls')),
    path('', views.index, name='index'),
]
