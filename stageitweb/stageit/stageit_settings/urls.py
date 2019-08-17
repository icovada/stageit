from django.urls import path

from . import views

urlpatterns = [
    path('terminalserver', views.TerminalServerFormView.as_view()),
    path('serialport', views.SerialPortFormView.as_view()),
]
