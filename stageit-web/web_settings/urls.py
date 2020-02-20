from django.urls import path

from . import views

urlpatterns = [
    path('terminalserver', views.terminalserver),
    path('terminalserver/add', views.TerminalServerCreate.as_view()),
    path('terminalserver/<uuid:pk>', views.TerminalServerUpdate.as_view()),
    path('serialport', views.serialport),
    path('serialport/add', views.SerialPortCreate.as_view()),
    path('serialport/<uuid:pk>', views.SerialPortUpdate.as_view()),
    path('filemanager/upload', views.upload_file),
    path('filemanager/', views.filemanager),
    path('remoteworker/', views.remoteworker),
    path('remoteworker/add', views.RemoteWorkerCreate.as_view()),
    path('remoteworker/<uuid:pk>', views.RemoteWorkerUpdate.as_view()),
    path('bootstrapconfig/', views.bootstrapconfig),
    path('bootstrapconfig/add', views.bootstrapconfigadd),
    path('bootstrapconfig/<uuid:uuid>', views.bootstrapconfigdetail),
]
