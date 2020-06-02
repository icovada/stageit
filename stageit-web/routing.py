from channels.routing import ProtocolTypeRouter, URLRouter
import web_interface.routing

application = ProtocolTypeRouter({
    'http': URLRouter(web_interface.routing.urlpatterns),
})