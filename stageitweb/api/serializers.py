from rest_framework import serializers
import stageitweb.stageit.models as models
from rest_framework import generics

import pickle

class PickledData(serializers.Field):
    """
    Turn pickled data to original and back
    """
    def to_representation(self, value):
        return pickle.loads(value)

    def to_internal_value(self, value):
        return pickle.dumps(value)

class FkTemplateSerializer(serializers.Field):
    """
    Serialize template pkid to string
    """
    def to_representation(self, value):
        return value.pkid

    def to_internal_value(self, value):
        return models.Templates.objects.get(pkid=value)

class FkHistorySerializer(serializers.Field):
    """
    Serialize template pkid to string
    """
    def to_representation(self, value):
        return value.pkid

    def to_internal_value(self, value):
        return models.History.objects.get(pkid=value)


class TemplatesSerializer(serializers.Serializer):
    """Defines templates table."""
    pkid = serializers.UUIDField(format='hex_verbose', required=False)
    description = serializers.CharField(max_length=50)
    filepath = serializers.CharField(max_length=256)
    installmode = serializers.CharField(max_length=20)
    name = serializers.CharField(max_length=50)
    platform = serializers.CharField(max_length=30)
    poststaging = serializers.CharField(max_length=1000)
    template = serializers.CharField(max_length=500000)
    templatevalues = serializers.JSONField()

    def create(self, validated_data):
        from uuid import uuid4
        pkid = uuid4()
        data = {**validated_data, 'pkid': pkid}

        return models.Templates.objects.create(**data)

    def update(self, instance, validated_data):
        instance.__dict__ = {**instance.__dict__, **validated_data}
        instance.save()

        return instance

class HistorySerializer(serializers.Serializer):
    """Defines history table."""
    pkid = serializers.UUIDField(format='hex_verbose', required=False)
    dateend = serializers.DateTimeField
    datestart = serializers.DateTimeField
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

    def create(self, validated_data):
        from uuid import uuid4

        validated_data['pkid'] = validated_data.get('pkid', uuid4())

        return models.History.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.__dict__ = {**instance.__dict__, **validated_data}
        instance.save()

        return instance


    
class TasksSerializer(serializers.Serializer):
    """Defines tasks table."""
    pkid = serializers.UUIDField(format='hex_verbose', required=False)
    description = serializers.CharField(max_length=50)
    fktemplate = FkTemplateSerializer(required=False)
    taskvalues = serializers.JSONField()
    
    def create(self, validated_data):
        from uuid import uuid4
        pkid = str(uuid4())
        data = {**validated_data, 'pkid': pkid}

        return models.Tasks.objects.create(**data)

    def update(self, instance, validated_data):
        instance.__dict__ = {**instance.__dict__, **validated_data}
        instance.save()

        return instance


class LogSerializer(serializers.Serializer):
    """Defines log table"""
    fkhistory = FkHistorySerializer()
    sequence = serializers.IntegerField()
    log = serializers.CharField() 

    def get_queryset(self, **kwargs):

        fkhistory = self.kwargs.get(self.lookup_url_kwarg)
        return models.Log.objects.filter(fkhistory=fkhistory).order_by('sequence', 'asc')

    def create(self, validated_data):
        return models.Log.objects.create(**validated_data)

class TerminalServerSerializer(serializers.Serializer):
    pkid = serializers.UUIDField(format='hex_verbose', required=False)
    name = serializers.CharField()
    model = serializers.CharField()
    hostname = serializers.CharField()
    transport = serializers.CharField()
    username = serializers.CharField()
    password = serializers.CharField()

    def create(self, validated_data):
        from uuid import uuid4
        pkid = str(uuid4())
        data = {**validated_data, 'pkid': pkid}

        return models.TerminalServer.objects.create(**data)


class SerialPortSerializer(serializers.Serializer):
    pkid = serializers.UUIDField(format='hex_verbose', required=False)
    fkterminalserver = serializers.PrimaryKeyRelatedField(queryset=models.TerminalServer.objects)
    transport = serializers.CharField()
    port = serializers.IntegerField()
    line = serializers.IntegerField()

    def create(self, validated_data):
        from uuid import uuid4
        pkid = str(uuid4())
        data = {**validated_data, 'pkid': pkid}

        return models.SerialPort.objects.create(**data)