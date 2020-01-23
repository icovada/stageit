from django.urls import path

from . import views

urlpatterns = [
    path('terminalserver', views.terminalserver),
    path('terminalserver/add', views.TerminalServerCreate.as_view()),
    path('terminalserver/<uuid:pk>', views.TerminalServerUpdate.as_view()),
    path('terminalserver/<uuid:pk>/delete', views.TerminalServerDelete.as_view()),
    path('serialport', views.serialport),
    path('serialport/add', views.SerialPortCreate.as_view()),
    path('serialport/<uuid:pk>', views.SerialPortUpdate.as_view()),
    path('filemanager/upload', views.upload_file),
    path('filemanager/', views.filemanager),
    path('bootstrapconfig/', views.bootstrapconfig),
    path('bootstrapconfig/add', views.BootstrapConfigCreate.as_view()),
    path('bootstrapconfig/<uuid:pk>', views.BootstrapConfigUpdate.as_view()),
    path('bootstrapconfig/<uuid:pk>/delete', views.BootstrapConfigDelete.as_view())
]
