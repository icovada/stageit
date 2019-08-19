import jsonfield
from django.db import models
from uuid import uuid4

# Create your models here.
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
    templatevalues = jsonfield.JSONField()

    def __str__(self):
        return('{} - {}'.format(str(self.pkid)[:5], self.name))

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
    templatevalues = jsonfield.JSONField(null=True)
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
    taskvalues = jsonfield.JSONField(null=True)

    def __str__(self):
        return('{} based on {}'.format(self.description, self.fktemplate))

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