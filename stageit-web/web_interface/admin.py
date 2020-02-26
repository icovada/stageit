from django.contrib import admin
import web_interface.models as models
# Register your models here.

admin.site.register(models.Template)
admin.site.register(models.History)
admin.site.register(models.Task)
admin.site.register(models.Log)
admin.site.register(models.TerminalServer)
admin.site.register(models.SerialPort)
admin.site.register(models.BootstrapConfig)
admin.site.register(models.RemoteWorker)