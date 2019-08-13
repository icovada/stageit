from rest_framework import serializers
from stageitweb.stageit.models import Templates, History, Tasks, Log
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
        return Templates.objects.get(pkid=value)

class FkHistorySerializer(serializers.Field):
    """
    Serialize template pkid to string
    """
    def to_representation(self, value):
        return value.pkid

    def to_internal_value(self, value):
        return History.objects.get(pkid=value)


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

        return Templates.objects.create(**data)

    def update(self, instance, validated_data):
        instance.__dict__ = {**instance.__dict__, **validated_data}
        instance.save()

        return instance

class HistorySerializer(serializers.Serializer):
    """Defines history table."""
    pkid = serializers.UUIDField(format='hex_verbose', required=False)
    dateend = serializers.DateTimeField
    datestart = serializers.DateTimeField
    description = serializers.CharField(max_length=50)
    installmode = serializers.CharField(max_length=20)
    model = serializers.CharField(max_length=50)
    os_version = serializers.CharField(max_length=300)
    rundata = serializers.JSONField()
    serial = serializers.CharField(max_length=20)
    serial_number = serializers.CharField(max_length=50)
    template = serializers.CharField(max_length=20000)
    templatevalues = serializers.JSONField()
    vendor = serializers.CharField(max_length=30)

    def create(self, validated_data):
        from uuid import uuid4
        pkid = uuid4()
        data = {**validated_data, 'pkid': pkid}

        return History.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.__dict__ = {**instance.__dict__, **validated_data}
        instance.save()

        return instance


    
class TasksSerializer(serializers.Serializer):
    """Defines tasks table."""
    pkid = serializers.UUIDField(format='hex_verbose', required=False)
    description = serializers.CharField(max_length=50)
    fktemplate = FkTemplateSerializer()
    taskvalues = serializers.JSONField()
    
    def create(self, validated_data):
        from uuid import uuid4
        pkid = str(uuid4())
        data = {**validated_data, 'pkid': pkid}

        return Tasks.objects.create(**data)

    def update(self, instance, validated_data):
        instance.__dict__ = {**instance.__dict__, **validated_data}
        instance.save()

        return instance


class LogSerializer(serializers.Serializer):
    """Defines log table"""
    #fkhistory = FkHistorySerializer(required=False, read_only=True)
    sequence = serializers.IntegerField(read_only=True)
    log = serializers.CharField(read_only=True) 

    def get_queryset(self, **kwargs):
        """
        List only logs relevant to history row and after line number
        URL format: /api/logs/<fkhistory>/<lastrow>
        """
        fkhistory = self.kwargs.get(self.lookup_url_kwarg)
        return Log.objects.filter(fkhistory=fkhistory).order_by('sequence', 'asc')
