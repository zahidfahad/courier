from .models import *
from django import forms


class WalletModelForm(forms.ModelForm):
    class Meta:
        model = WalletModel
        fields = ['user', 'amount', 'tr_method']


class PackageForm(forms.ModelForm):
    class Meta:
        model = Package
        fields = ['name', 'description', 'price', 'activate']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control',"rows":5, "cols":20}),
            }


class ReferPriceForm(forms.ModelForm):
    class Meta:
        model = ReferPrice
        fields = ['refer_type', 'price']


class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQModel
        fields = ['faq_type', 'question', 'answer']


class PricesForm(forms.ModelForm):
    class Meta:
        model = Prices
        fields = '__all__'
