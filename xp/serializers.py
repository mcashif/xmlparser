from rest_framework import serializers
from .models import XMLFile

# Serializers define the API representation.
class XMLSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = XMLFile
        fields = ('file_name','file_data')
