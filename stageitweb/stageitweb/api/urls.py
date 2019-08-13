from django.urls import path, include
from rest_framework import routers
from stageitweb.api import views

router = routers.DefaultRouter()
router.register(r'templates', views.TemplatesViewSet)
router.register(r'tasks', views.TasksViewSet)
router.register(r'history', views.HistoryViewSet)
router.register(r'log', views.LogViewSet)

urlpatterns = [
    path('convertjinja', views.convertjinja, name='convertjinja'),
    path('', include(router.urls)),
]
