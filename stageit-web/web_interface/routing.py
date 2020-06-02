from django.conf.urls import url
from channels.routing import URLRouter
from channels.http import AsgiHandler
from channels.auth import AuthMiddlewareStack
import django_eventstream

urlpatterns = [
    url(r'^events/history/(?P<obj_id>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})', AuthMiddlewareStack(URLRouter(django_eventstream.routing.urlpatterns)), {'format-channels': ['history-{obj_id}']}),
    url(r'^events/notifications', AuthMiddlewareStack(URLRouter(django_eventstream.routing.urlpatterns)), {'channels': ['notifications']}),
    url(r'', AsgiHandler),
]
