from django.db import models
from uuid import uuid4
from django.urls import reverse
import ast

# Create your models here.
class BootstrapConfig(models.Model):
    pkid = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    name = models.TextField()
    description = models.TextField()
    bootstraptemplate = models.TextField()
    values = models.TextField()

    def __str__(self):
        return('{} - {}'.format(self.name, self.description))

    def get_absolute_url(self):
        return(str(self.pkid))

    def save(self, *args, **kwargs):
        self.values = ast.literal_eval(self.values)
        super().save(*args, **kwargs)

class Template(models.Model):
    """Defines templates table."""
    pkid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    description = models.TextField(max_length=50)
    filepath = models.TextField(max_length=256, null=True)
    installmode = models.TextField(max_length=20)
    name = models.TextField(max_length=50, unique=True, null=False)
    platform = models.TextField(max_length=30, null=False)
    poststaging = models.TextField(max_length=1000)
    template = models.TextField(max_length=500000)
    templatevalues = models.TextField()
    fkbootstrapconfig = models.ForeignKey(BootstrapConfig, models.PROTECT, null=True)

    def __str__(self):
        return('{} - {}'.format(str(self.pkid)[:5], self.name))

    def save(self, *args, **kwargs):
        self.templatevalues = ast.literal_eval(self.templatevalues)
        super().save(*args, **kwargs)

class History(models.Model):
    """Defines history table."""
    pkid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    dateend = models.DateTimeField(null=True)
    datestart = models.DateTimeField(null=True)
    description = models.TextField(max_length=50)
    installmode = models.TextField(max_length=20)
    model = models.TextField(max_length=50)
    os_version = models.TextField(max_length=300)
    rundata = models.BinaryField(max_length=1024000, editable=True, null=True)
    serial = models.TextField(max_length=20)
    template = models.TextField(max_length=20000)
    templatevalues = models.TextField(null=True)
    vendor = models.TextField(max_length=30)
    status = models.TextField(null=True)
    workerid = models.TextField(null=True)
    fktask = models.TextField(null=False)
    fkserialport = models.UUIDField()

class Task(models.Model):
    """Defines tasks table."""
    pkid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    description = models.TextField(max_length=50)
    fktemplate = models.ForeignKey(Template, on_delete=models.CASCADE)
    taskvalues = models.TextField(null=True)

    def __str__(self):
        return('{} based on {}'.format(self.description, self.fktemplate))

    def save(self, *args, **kwargs):
        self.taskvalues = ast.literal_eval(self.taskvalues)
        super().save(*args, **kwargs)

class Log(models.Model):
    """Define staging Log format"""
    fkhistory = models.ForeignKey(History, on_delete=models.CASCADE)
    sequence = models.PositiveIntegerField()
    log = models.TextField(null=True)
    logdate = models.DateTimeField(auto_now_add=True)

class TerminalServer(models.Model):
    pkid = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    name = models.TextField()
    model = models.TextField()
    hostname = models.TextField(unique=True)
    transport = models.TextField()
    username = models.TextField()
    password = models.TextField()

    def __str__(self):
        return('{} - {}'.format(self.name, self.hostname))

class SerialPort(models.Model):
    pkid = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    fkterminalserver = models.ForeignKey(TerminalServer, on_delete=models.PROTECT)
    transport = models.TextField()
    port = models.IntegerField()
    line = models.IntegerField()
    
    class Meta:
        unique_together = ('fkterminalserver', 'port',)

    def __str__(self):
        return('{} - {}'.format(self.fkterminalserver, self.line))

class Firmware(models.Model):
    pkid = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    filename = models.TextField()
    md5 = models.TextField()
    sha256 = models.TextField()
