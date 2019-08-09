from django.urls import path, include
from rest_framework import routers
from stageitweb.api import views

router = routers.DefaultRouter()
router.register(r'templatesr', views.TemplatesViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('templates/', views.templates_list),
    path('templates/<uuid:uuid>', views.templates_detail)
]
