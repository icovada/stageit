from django.contrib import admin
import stageitweb.stageit.models as models
# Register your models here.

admin.site.register(models.Template)
admin.site.register(models.History)
admin.site.register(models.Task)
admin.site.register(models.Log)
admin.site.register(models.TerminalServer)
admin.site.register(models.SerialPort)