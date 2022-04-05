from django import forms
from .models import *


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['receiver', 'payment', 'reference_id', 'receiver_Contact', 'receiver_Email', 'area', 'weight', 'service', 'product_Type',
                  'contents', 'quantity', 'package', 'amount', 'priority', 'delivery_time', 'paid', 'pick_up_latitude', 'pick_up_longitude', 'delivery_latitude', 'delivery_longitude', 'pickup_finish', 'change_latitude', 'change_longitude']


class CancelOrderForm(forms.ModelForm):
    class Meta:
        model = CancelOrder
        fields = ['user', 'receiver', 'receiver_Address', 'receiver_Contact', 'receiver_Email', 'payment', 'reference_id', 'service',
                  'product_Type', 'contents', 'quantity', 'package', 'amount', 'priority', 'paid', 'delivery_now', 'delivery_later', 'created',
                  'pick_up_latitude', 'pick_up_longitude', 'delivery_latitude', 'delivery_longitude']
