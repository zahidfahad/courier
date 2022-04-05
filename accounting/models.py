from django.db import models
import datetime
from django.shortcuts import reverse
from user.models import User
# Create your models here.


class WalletModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.CharField(max_length=100, blank=True, null=True, default=0)
    tr_method = models.CharField(max_length=100, blank=True, null=True)
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True, related_name="rcv")
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True, related_name="sender")
    created_on = models.DateField(auto_now_add=True)
    tran_id = models.CharField(max_length=15)

    def __str__(self):
        return self.user.username


class TransactionModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tran_id = models.CharField(max_length=15)
    val_id = models.CharField(max_length=75)
    card_type = models.CharField(max_length=150)
    store_amount = models.DecimalField(max_digits=10, decimal_places=2)
    card_no = models.CharField(max_length=55, null=True)
    bank_tran_id = models.CharField(max_length=155, null=True)
    status = models.CharField(max_length=55)
    tran_date = models.DateTimeField()
    currency = models.CharField(max_length=10)
    card_issuer = models.CharField(max_length=255)
    card_brand = models.CharField(max_length=15)
    card_issuer_country = models.CharField(max_length=55)
    card_issuer_country_code = models.CharField(max_length=55)
    currency_rate = models.DecimalField(max_digits=10, decimal_places=2)
    verify_sign = models.CharField(max_length=155)
    verify_sign_sha2 = models.CharField(max_length=255)
    risk_level = models.CharField(max_length=15)
    risk_title = models.CharField(max_length=25)
    reason = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return self.tran_id


class Package(models.Model):
    name = models.CharField(max_length=100, blank=False,
                            null=False, unique=True)
    description = models.CharField(max_length=100, blank=False, unique=False)
    price = models.CharField(max_length=6, blank=False, unique=False)
    activate = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class ReferPrice(models.Model):
    refers = [
        ('driver', 'driver'),
        ('delivery man', 'delivery man'),
        ('merchant', 'merchant'),
        ('agent', 'agent'),
        ('user', 'user')
    ]
    refer_type = models.CharField(max_length=100, choices=refers)
    price = models.CharField(max_length=4, blank=False,
                             null=False, unique=False)

    def __str__(self):
        return self.refer_type


class FAQModel(models.Model):
    types = [
        ('App', 'App'),
        ('Booking', 'Booking')
    ]
    faq_type = models.CharField(max_length=100, choices=types, blank=False)
    question = models.CharField(max_length=200, blank=False, unique=True)
    answer = models.TextField(max_length=1000, blank=False)

    def __str__(self):
        return self.question

    def get_absolute_url(self):
        return reverse('CreateFAQ')


class Prices(models.Model):
    inside_dhaka = models.CharField(max_length=100, blank=False, null=False)
    dhaka_suburb = models.CharField(max_length=100, blank=False, null=False)
    outside_dhaka = models.CharField(max_length=100, blank=False, null=False)
    extra = models.CharField(max_length=100, blank=False, null=False)
