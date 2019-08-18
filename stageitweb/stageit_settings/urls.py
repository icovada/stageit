from django.urls import path

from . import views

urlpatterns = [
    path('terminalserver', views.terminalserver),
    path('terminalserver/add', views.TerminalServerFormView.as_view()),
    path('terminalserver/<uuid:uuid>', views.edit_terminal_server),
    path('serialport', views.serialport),
    path('serialport/add', views.SerialPortFormView.as_view()),
    path('serialport/<uuid:uuid>', views.edit_serial_port),
    path('filemanager/upload', views.upload_file),
    path('filemanager/', views.filemanager)
]
