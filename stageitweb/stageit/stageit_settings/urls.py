from django.urls import path

from . import views

urlpatterns = [
    path('terminalserver', views.terminalserver),
    path('terminalserver/add', views.TerminalServerFormView.as_view()),
    path('terminalserver/<uuid:uuid>', views.edit_terminal_server),
    path('serialport', views.SerialPortFormView.as_view()),
]
