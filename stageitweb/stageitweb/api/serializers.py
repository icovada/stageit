from rest_framework import serializers
from stageitweb.stageit.models import Templates


class TemplatesSerializer(serializers.Serializer):
    """Defines templates table."""
    pkid = serializers.UUIDField
    description = serializers.CharField(max_length=50)
    filepath = serializers.CharField(max_length=256)
    installmode = serializers.CharField(max_length=20)
    name = serializers.CharField(max_length=50)
    platform = serializers.CharField(max_length=30)
    poststaging = serializers.CharField
    template = serializers.CharField
    templatevalues = serializers.Field

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