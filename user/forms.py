from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, DateInput
from django.db import transaction
from user.models import *


class UserCreation(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'contact', 'address', 'password1', 'password2', 'user_pic',
                  'email', 'address2', 'postal_code', 'city', 'is_driver', 'is_delivery_man', 'is_merchant', 'is_agent', 'is_user']
        widgets = {
            'city': forms.Select(attrs={'class': 'form-control'}),
        }


class Admin_Profile_Edit(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name',
                  'user_pic', 'contact', 'city', 'quote']
        widgets = {
            'city': forms.Select(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'quote': forms.TextInput(attrs={'class': 'form-control'}),
            'user_pic': forms.FileInput(attrs={'class': 'form-control'}),
        }


class Driver_profile_Edit(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'quote', 'contact', 'contact2',
                  'contact3', 'contact4', 'address', 'user_pic', 'address2', 'postal_code', 'city']
        widgets = {
            'city': forms.Select(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'contact2': forms.TextInput(attrs={'class': 'form-control'}),
            'contact3': forms.TextInput(attrs={'class': 'form-control'}),
            'contact4': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'address2': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'quote': forms.TextInput(attrs={'class': 'form-control'}),
            'user_pic': forms.FileInput(attrs={'class': 'form-control'}),
        }


class Delivery_man_profile_Edit(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'quote', 'contact', 'contact2',
                  'contact3', 'contact4', 'address', 'user_pic', 'address2', 'postal_code', 'city', 'latitude', 'longitude']
        widgets = {
            'city': forms.Select(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'contact2': forms.TextInput(attrs={'class': 'form-control'}),
            'contact3': forms.TextInput(attrs={'class': 'form-control'}),
            'contact4': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'address2': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'quote': forms.TextInput(attrs={'class': 'form-control'}),
            'user_pic': forms.FileInput(attrs={'class': 'form-control'}),
        }


class Merchant_profile_Edit(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'quote', 'contact', 'contact2',
                  'contact3', 'contact4', 'address', 'user_pic', 'address2', 'postal_code', 'city']
        widgets = {
            'city': forms.Select(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'contact2': forms.TextInput(attrs={'class': 'form-control'}),
            'contact3': forms.TextInput(attrs={'class': 'form-control'}),
            'contact4': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'address2': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'quote': forms.TextInput(attrs={'class': 'form-control'}),
            'user_pic': forms.FileInput(attrs={'class': 'form-control'}),
        }


class User_profile_Edit(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'quote', 'contact', 'contact2',
                  'contact3', 'contact4', 'address', 'user_pic', 'address2', 'postal_code', 'city']
        widgets = {
            'city': forms.Select(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'contact2': forms.TextInput(attrs={'class': 'form-control'}),
            'contact3': forms.TextInput(attrs={'class': 'form-control'}),
            'contact4': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'address2': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'quote': forms.TextInput(attrs={'class': 'form-control'}),
            'user_pic': forms.FileInput(attrs={'class': 'form-control'}),
        }


class Agent_profile_Edit(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'quote', 'contact', 'contact2',
                  'contact3', 'contact4', 'address', 'user_pic', 'address2', 'postal_code', 'city']
        widgets = {
            'city': forms.Select(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'contact2': forms.TextInput(attrs={'class': 'form-control'}),
            'contact3': forms.TextInput(attrs={'class': 'form-control'}),
            'contact4': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'address2': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'quote': forms.TextInput(attrs={'class': 'form-control'}),
            'user_pic': forms.FileInput(attrs={'class': 'form-control'}),
        }


class DriverVehicle(forms.ModelForm):
    class Meta:
        model = User
        fields = ['driving_license', 'vehicle_type', 'vehicle_no']
        widgets = {
            'vehicle_type': forms.Select(attrs={'class': 'form-control'}),
            'vehicle_no': forms.TextInput(attrs={'class': 'form-control'}),
            'driving_license': forms.FileInput(attrs={'class': 'form-control'}),
        }


class AdminMessage(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AdminMessage, self).__init__(*args, **kwargs)
        instance = kwargs.pop('instance', User)
        self.fields["receiver"].queryset = User.objects.filter(
            is_superuser=False)

    class Meta:
        model = Message
        fields = ['sender', 'receiver', 'msg']
        widgets = {
            'sender': forms.Select(attrs={'class': 'form-control'}),
            'receiver': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'msg': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'type messages', 'required': 'true'}),
        }


class EmailChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'required': 'true'}),
        }
