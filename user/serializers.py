from rest_framework import serializers, fields
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class Notifications(serializers.ModelSerializer):
    user = UserSerializer()
    driver = UserSerializer()

    class Meta:
        model = Notification
        fields = '__all__'


class ReferralModel(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = ReferralModel
        fields = '__all__'


class ReferHistory(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = ReferHistory
        fields = '__all__'


class Ratings(serializers.ModelSerializer):
    rated_user = UserSerializer()
    rating_giver = UserSerializer()

    class Meta:
        model = Ratings
        fields = '__all__'




# api's for mobile app
class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer
    receiver = UserSerializer

    class Meta:
        model = Message
        fields = '__all__'


class ResponseMSGserializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'
        depth = 2


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=100)

    class Meta:
        fields = ['username', 'password']




class ChoiceField(serializers.ChoiceField):

    def to_representation(self, obj):
        if obj == '' and self.allow_blank:
            return obj
        return self._choices[obj]

    def to_internal_value(self, data):
        # To support inserts with the value
        if data == '' and self.allow_blank:
            return ''

        for key, val in self._choices.items():
            if val == data:
                return key
        self.fail('invalid_choice', input=data)

class RegisterSerializer(serializers.ModelSerializer):
    city = ChoiceField(choices=User.CITIES)
    password1 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'contact', 'address','city', 'password', 'password1',
                  'email', 'address2', 'postal_code', 'is_driver', 'is_delivery_man', 'user_pic', 'is_merchant',
                  'is_agent', 'is_user']

        extra_kwargs = {'password': {'write_only': True},
                        'city': {'required': True}
                        }

    def create(self, validated_data):
        user = User.objects.create(first_name=validated_data['first_name'], last_name=validated_data['last_name'],
                                   contact=validated_data['contact'], address=validated_data['address'],
                                   email=validated_data['email'], address2=validated_data['address2'],
                                   postal_code=validated_data['postal_code'], is_driver=validated_data['is_driver'],
                                   is_delivery_man=validated_data['is_delivery_man'], is_merchant=validated_data['is_merchant'],
                                   is_agent=validated_data['is_agent'], is_user=validated_data['is_user'],
                                    username=validated_data['username'], city = validated_data['city']
                                   )
        user.set_password(validated_data['password1'])
        user.save()
        return user

class AccountApprove(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['is_active','username']
