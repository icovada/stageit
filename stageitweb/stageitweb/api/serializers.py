from rest_framework import serializers
from stageitweb.stageit.models import Templates

import pickle

class PickledData(serializers.Field):
    """
    Turn pickled data to original and back
    """
    def to_representation(self, value):
        return pickle.loads(value)

    def to_internal_value(self, value):
        return pickle.dumps(value)

class TemplatesSerializer(serializers.Serializer):
    """Defines templates table."""
    pkid = serializers.UUIDField(format='hex_verbose')
    description = serializers.CharField(max_length=50)
    filepath = serializers.CharField(max_length=256)
    installmode = serializers.CharField(max_length=20)
    name = serializers.CharField(max_length=50)
    platform = serializers.CharField(max_length=30)
    poststaging = serializers.CharField(max_length=1000)
    template = serializers.CharField(max_length=500000)
    templatevalues = PickledData(read_only=False)

    def create(self, validated_data):
        from uuid import uuid4
        pkid = uuid4()
        data = {'pkid': pkid, **validated_data}

        return Templates.objects.create(**data)

    def update(self, instance, validated_data):
        instance.description = validated_data.get('description', instance.description)
        instance.filepath = validated_data.get('filepath', instance.filepath)
        instance.installmode = validated_data.get('installmode', instance.installmode)
        instance.name = validated_data.get('name', instance.name)
        instance.platform = validated_data.get('platform', instance.platform)
        instance.poststaging = validated_data.get('poststaging', instance.poststaging)
        instance.template = validated_data.get('template', instance.template)
        instance.templatevalues = validated_data.get('templatevalues', instance.templatevalues)
        instance.save()

        return instance
