from rest_framework import serializers
from .models import *
from user.serializers import UserSerializer
from accounting.models import Package


class SelectPackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    driver = UserSerializer()

    class Meta:
        model = Order
        fields = '__all__'


class CancelOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = CancelOrder
        fields = '__all__'


class CashCollectionSerializer(serializers.ModelSerializer):
    order = NotificationSerializer()
    driver = UserSerializer()

    class Meta:
        model = CashCollection
        fields = '__all__'
