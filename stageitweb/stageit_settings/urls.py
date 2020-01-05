from django.urls import path

from . import views

urlpatterns = [
    path('terminalserver', views.terminalserver),
    path('terminalserver/add', views.TerminalServerCreate.as_view()),
    path('terminalserver/<uuid:pk>', views.TerminalServerUpdate.as_view()),
    path('serialport', views.serialport),
    path('serialport/add', views.SerialPortFormView.as_view()),
    path('serialport/<uuid:pk>', views.edit_serial_port),
    path('filemanager/upload', views.upload_file),
    path('filemanager/', views.filemanager),
    path('bootstrapconfig/', views.bootstrapconfig),
    path('bootstrapconfig/add', views.BootstrapConfigCreate.as_view()),
    path('bootstrapconfig/<uuid:pk>', views.BootstrapConfigUpdate.as_view()),
    path('bootstrapconfig/<uuid:pk>/delete', views.BootstrapConfigDelete.as_view())
]
