from rest_framework import serializers
from .models import *
from user.serializers import UserSerializer


class WalletModelSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = WalletModel
        fields = '__all__'


class TransactionModelSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = TransactionModel
        fields = '__all__'


class PackageModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = '__all__'


class ReferPriceModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferPrice
        fields = '__all__'


class FAQModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQModel
        fields = '__all__'


class PricesModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prices
        fields = '__all__'



