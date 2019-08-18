from rest_framework import serializers
import stageitweb.stageit.models as models
from rest_framework import generics


class TemplateSerializer(serializers.ModelSerializer):
    """Defines templates table."""
    pkid = serializers.UUIDField(format='hex_verbose', required=False)
    description = serializers.CharField(max_length=50)
    filepath = serializers.CharField(max_length=256, required=False)
    installmode = serializers.CharField(max_length=20)
    name = serializers.CharField(max_length=50)
    platform = serializers.CharField(max_length=30)
    poststaging = serializers.CharField(max_length=1000, required=False)
    template = serializers.CharField(max_length=500000)
    templatevalues = serializers.JSONField()

    class Meta:
        model = models.Template
        fields = '__all__'


class HistorySerializer(serializers.ModelSerializer):
    """Defines history table."""
    pkid = serializers.UUIDField(format='hex_verbose', required=False)
    dateend = serializers.DateTimeField()
    datestart = serializers.DateTimeField()
    description = serializers.CharField(max_length=50, required=False)
    installmode = serializers.CharField(max_length=20, required=False)
    model = serializers.CharField(max_length=50, required=False)
    os_version = serializers.CharField(max_length=300, required=False)
    rundata = serializers.JSONField(required=False)
    serial = serializers.CharField(max_length=20, required=False)
    serial_number = serializers.CharField(max_length=50, required=False)
    template = serializers.CharField(max_length=20000, required=False)
    templatevalues = serializers.JSONField(required=False)
    vendor = serializers.CharField(max_length=30, required=False)
    status = serializers.CharField(required=False)
    workerid = serializers.CharField(required=False)
    fktask = serializers.CharField(required=False)
    fkserialport = serializers.PrimaryKeyRelatedField(queryset=models.SerialPort.objects, required=False)

    class Meta:
        model = models.History
        fields = '__all__'

    
class TaskSerializer(serializers.ModelSerializer):
    """Defines tasks table."""
    pkid = serializers.UUIDField(format='hex_verbose', required=False)
    description = serializers.CharField(max_length=50)
    fktemplate = serializers.PrimaryKeyRelatedField(queryset=models.Template.objects, required=False)
    taskvalues = serializers.JSONField(required=False)

    class Meta:
        model = models.Task
        fields = '__all__'
    

class LogSerializer(serializers.ModelSerializer):
    """Defines log table"""
    fkhistory = serializers.PrimaryKeyRelatedField(queryset=models.History.objects)
    sequence = serializers.IntegerField()
    log = serializers.CharField() 

    class Meta:
        model = models.Log
        fields = '__all__'

    
class TerminalServerSerializer(serializers.ModelSerializer):
    pkid = serializers.UUIDField(format='hex_verbose', required=False)
    name = serializers.CharField()
    model = serializers.CharField()
    hostname = serializers.CharField()
    transport = serializers.CharField()
    username = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        model = models.TerminalServer
        fields = '__all__'

class SerialPortSerializer(serializers.ModelSerializer):
    pkid = serializers.UUIDField(format='hex_verbose', required=False)
    fkterminalserver = serializers.PrimaryKeyRelatedField(queryset=models.TerminalServer.objects)
    transport = serializers.CharField()
    port = serializers.IntegerField()
    line = serializers.IntegerField()

    class Meta:
        model = models.SerialPort
        fields = '__all__'