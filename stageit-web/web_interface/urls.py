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
    path('sandbox', views.sandbox),
    path('settings/', include('web_settings.urls')),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('', views.index, name='index'),
]
