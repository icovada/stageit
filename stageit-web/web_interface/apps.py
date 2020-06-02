from django.apps import AppConfig


class WebInterfaceConfig(AppConfig):
    name = 'web_interface'

    def ready(self):
        import web_interface.signals