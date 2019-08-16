from django.urls import path, include
from rest_framework import routers
from stageitweb.api import views

router = routers.DefaultRouter()
router.register(r'template', views.TemplatesViewSet)
router.register(r'task', views.TasksViewSet)
router.register(r'history', views.HistoryViewSet)
router.register(r'log', views.LogViewSet)
router.register(r'terminalserver', views.TerminalServerViewSet)
router.register(r'serialport', views.SerialPortViewSet)

urlpatterns = [
    path('convertjinja', views.convertjinja, name='convertjinja'),
    path('streamlogs/<uuid:uuid>', views.streamlogs, name='streamlogs'),
    path('', include(router.urls)),
]
