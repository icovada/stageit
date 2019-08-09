from django.db import models

# Create your models here.
class Templates(models.Model):
    """Defines templates table."""
    pkid = models.UUIDField(primary_key=True)
    description = models.TextField(max_length=50)
    filepath = models.TextField(max_length=256)
    installmode = models.TextField(max_length=20)
    name = models.TextField(max_length=50, unique=True, null=False)
    platform = models.TextField(max_length=30, null=False)
    poststaging = models.TextField(max_length=1000)
    template = models.TextField(max_length=500000)
    templatevalues = models.BinaryField(editable=True)

class History(models.Model):
    """Defines history table."""
    pkid = models.UUIDField(primary_key=True)
    dateend = models.DateTimeField
    datestart = models.DateTimeField
    description = models.TextField(max_length=50)
    installmode = models.TextField(max_length=20)
    model = models.TextField(max_length=50)
    os_version = models.TextField(max_length=300)
    rundata = models.BinaryField(max_length=1024000, editable=True)
    serial = models.TextField(max_length=20)
    serial_number = models.TextField(max_length=50)
    template = models.TextField(max_length=20000)
    templatevalues = models.BinaryField(editable=True)
    vendor = models.TextField(max_length=30)

class Tasks(models.Model):
    """Defines tasks table."""
    pkid = models.UUIDField(primary_key=True)
    description = models.TextField(max_length=50)
    fktemplate = models.ForeignKey(Templates, on_delete=models.CASCADE)
    taskvalues = models.BinaryField(editable=True)
