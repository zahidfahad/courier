from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime
from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework.authtoken.models import Token
# Create your models here.


class User(AbstractUser):
    CITIES = [
        ('Dhaka', 'Dhaka'),
        ('Rajshahi', 'Rajshahi'),
        ('Chittagong', 'Chittagong'),
        ('Sylhet', 'Sylhet'),
        ('Khulna', 'Khulna'),
        ('Mymensingh', 'Mymensingh'),
        ('Rangpur', 'Rangpur'),
        ('Dinajpur', 'Dinajpur'),
    ]

    Vehicle_type = [
        ('Truck', 'Truck'),
        ('Van', 'Van'),
        ('Bike', 'Bike')
    ]
    email = models.EmailField(unique=True)
    contact = models.CharField(null=False, blank=False, max_length=20)
    contact2 = models.CharField(null=True, blank=True, max_length=20)
    contact3 = models.CharField(null=True, blank=True, max_length=20)
    contact4 = models.CharField(null=True, blank=True, max_length=20)
    address = models.CharField(null=False, blank=False, max_length=100)
    address2 = models.CharField(null=True, blank=True, max_length=100)
    postal_code = models.CharField(null=True, blank=True, max_length=10)
    city = models.CharField(max_length=30, choices=CITIES)
    username = models.CharField(max_length=200, unique=True)
    user_pic = models.ImageField(upload_to='media/images/')
    n_id = models.CharField(max_length=100)
    quote = models.CharField(max_length=250, blank=True,
                             null=True, default='Bio Here. . .')

    driving_license = models.ImageField(upload_to='media/documents/')
    vehicle_type = models.CharField(max_length=30, choices=Vehicle_type)
    vehicle_no = models.CharField(max_length=50)

    latitude = models.CharField(max_length=100, default=0)
    longitude = models.CharField(max_length=100, default=0)

    is_driver = models.BooleanField(default=False)
    is_delivery_man = models.BooleanField(default=False)
    is_merchant = models.BooleanField(default=False)
    is_agent = models.BooleanField(default=False)
    is_user = models.BooleanField(default=False)
    is_available = models.BooleanField(default=False)

    verification_code = models.CharField(max_length=100, blank=True, null=True)
    #virification_code can only be used once
    one_time_logic = models.IntegerField(blank=True,null=True,default = 0,validators=[
                                         MaxValueValidator(1),
                                         MinValueValidator(0),
                                        ])

    def __str__(self):
        return self.username

    @property
    def photo_url(self):
        if self.user_pic and hasattr(self.user_pic, 'url'):
            return self.user_pic.url


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    driver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='driver_name', blank=True, null=True)
    text = models.CharField(max_length=200, blank=True, null=True, default='')

    is_seen = models.BooleanField(default=False)
    is_activated = models.BooleanField(default=False)
    order_id = models.CharField(
        max_length=20, blank=True, null=True, default='')

    accept_user = models.BooleanField(default=False)
    pickup_finish = models.BooleanField(default=False)
    change_address = models.BooleanField(default=False)
    finish = models.BooleanField(default=False)

    is_payment = models.BooleanField(default=False)
    is_transfer = models.BooleanField(default=False)
    is_manged = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class ReferralModel(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    code = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.user.username


class ReferHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=100, blank=False, null=True)
    amount = models. CharField(max_length=50, blank=False, default=0)
    created_on = models.DateField(auto_now_add=True)


class Message(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user', blank=True, null=True)
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='to_user', blank=True, null=True)
    msg = models.CharField(max_length=1000, blank=True, null=True)
    sent = models.DateTimeField(auto_now_add=True)
    mark_as_read = models.BooleanField(default=False)

    # def __str__(self):
    #     return self.sender.username + ' messaged ' + self.receiver.username


class Ratings(models.Model):
    rated_user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True, related_name='user_to_be_rated')
    rating_giver = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True, related_name='user_who_is_rating')
    storing_prev_now_rated_value = models.FloatField(
        null=True, blank=True, default=1.0)
    avg_rating = models.FloatField(null=True, blank=True, default=1.0)
    count = models.FloatField(blank=True, null=True, default=1.0)
    rated_number = models.FloatField(blank=True, null=True, default=1.0,
                                     validators=[
                                         MaxValueValidator(5),
                                         MinValueValidator(1),
                                     ]
                                     )

    def __str__(self):
        return self.rated_user.username + 's average rating = ' + str(self.avg_rating)


@receiver(post_save, sender=User)
def create_ratings(sender, instance, created, **kwargs):
    if created:
        if instance.is_delivery_man or instance.is_driver:
            Ratings.objects.create(rated_user=instance)


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
