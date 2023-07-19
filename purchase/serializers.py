from rest_framework import serializers

from purchase.models import Purchase


class PurchaseSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.id')
    owner_username = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Purchase
        fields = '__all__'
