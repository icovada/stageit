from django.urls import path

from . import views

urlpatterns = [
    path('', views.TerminalServerFormView.as_view()),
]
