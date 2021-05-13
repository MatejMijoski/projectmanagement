from rest_framework import serializers
from FilesApp.models import Files


class FileSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source='owner.email')

    class Meta:
        model = Files
        fields = ('id', 'name', 'owner', 'size', 'path', 'created_at')


class FilePostSerializer(serializers.ModelSerializer):
    file = serializers.FileField()

    class Meta:
        model = Files
        fields = ('name', 'file')
