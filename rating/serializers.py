from rest_framework import serializers

from rating.models import Mark


class MarkSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.id')
    owner_username = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Mark
        fields = '__all__'


