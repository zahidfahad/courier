from django.db import models
from user.models import *
from accounting.models import *
# Create your models here.


class Order(models.Model):
    productType = [
        ('Document', 'Document'),
        ('Parcel', 'Parcel'),
        ('Box', 'Box')
    ]
    serviceType = [
        ('Home', 'Home delivery'),
        ('Office', 'Office delivery'),
        ('Pick up from office', 'Pick up from office'),
    ]
    delivery_StatusType = [
        ('Return', 'Return'),
        ('Delivering', 'Delivering'),
        ('Pending', 'Pending'),
        ('Complete', 'Complete')
    ]
    statustype = [
        ('Paid', 'Paid'),
        ('Cash on delivery', 'Cash on delivery')
    ]

    status = [
        ('Instant', 'Instant'),
        ('Same Day', 'Same Day'),
        ('Others', 'Others')
    ]
    payment_types = [
        ('Cash', 'Cash'),
        ('Wallet', 'Wallet'),
        ('Online', 'Online')
    ]
    CHOICE_AREA = [
        ('Inside Dhaka', 'Inside Dhaka'),
        ('Dhaka Suburb', 'Dhaka Suburb'),
        ('Outside Dhaka', 'Outside Dhaka')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    receiver = models.CharField(max_length=100, blank=False, unique=False)
    receiver_Contact = models.CharField(
        max_length=20, blank=False, unique=False)
    receiver_Email = models.CharField(
        max_length=100, blank=False, unique=False)

    payment = models.CharField(
        max_length=100, choices=payment_types, blank=False)

    area = models.CharField(
        max_length=100, choices=CHOICE_AREA, blank=True, null=True)
    weight = models.CharField(max_length=100, blank=True, null=True)
    service = models.CharField(choices=serviceType,  max_length=100)
    product_Type = models.CharField(choices=productType, max_length=100)
    contents = models.CharField(max_length=100, blank=False, unique=False)
    quantity = models.CharField(max_length=100, blank=False, unique=False)

    package = models.ForeignKey(
        Package, on_delete=models.CASCADE, blank=True, null=True)
    priority = models.CharField(
        choices=status, blank=True, null=True, max_length=20)
    amount = models.CharField(max_length=100, blank=True, unique=False)
    delivery_Status = models.CharField(
        choices=delivery_StatusType, blank=True, null=True, max_length=50)

    paid = models.BooleanField(default=False)
    reference_id = models.CharField(max_length=100, blank=True, unique=True)
    delivery_time = models.DateField(blank=True, null=True)
    created = models.DateField(auto_now_add=True)
    tran_id = models.CharField(max_length=20, blank=True, null=True)
    driver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='driver', blank=True, null=True)
    driver_amount = models.CharField(max_length=5, blank=False, default='0')

    delivery_now = models.DateField(auto_now_add=True)
    delivery_later = models.DateField(blank=True, null=True)

    accept = models.BooleanField(default=False)

    start = models.BooleanField(blank=True, null=True)
    finish = models.BooleanField(blank=True, null=True)

    pick_up_latitude = models.CharField(blank=True, null=True, max_length=50)
    pick_up_longitude = models.CharField(blank=True, null=True, max_length=50)

    delivery_latitude = models.CharField(blank=True, null=True, max_length=50)
    delivery_longitude = models.CharField(blank=True, null=True, max_length=50)

    otp = models.CharField(max_length=10, blank=True, null=True)

    pickup_finish = models.BooleanField(default=False)
    approve_change_delivery_address = models.BooleanField(
        blank=True, null=True, default=False)

    confirm_change_delivery_address = models.BooleanField(
        blank=True, null=True, default=False)

    change_latitude = models.CharField(blank=True, null=True, max_length=100)
    change_longitude = models.CharField(blank=True, null=True, max_length=100)

    def __str__(self):
        return self.user.username


class CashCollection(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    driver = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.CharField(max_length=5, blank=False)
    created_on = models.DateField(auto_now_add=True)


class CancelOrder(models.Model):
    productType = [
        ('Document', 'Document'),
        ('Parcel', 'Parcel'),
        ('Box', 'Box')
    ]
    serviceType = [
        ('Home', 'Home delivery'),
        ('Office', 'Office delivery'),
        ('Pick up from office', 'Pick up from office'),
    ]
    delivery_StatusType = [
        ('Return', 'Return'),
        ('Delivering', 'Delivering'),
        ('Pending', 'Pending'),
        ('Complete', 'Complete')
    ]
    statustype = [
        ('Paid', 'Paid'),
        ('Cash on delivery', 'Cash on delivery')
    ]

    status = [
        ('Instant', 'Instant'),
        ('Same Day', 'Same Day'),
        ('Others', 'Others')
    ]
    payment_types = [
        ('Cash', 'Cash'),
        ('Wallet', 'Wallet'),
        ('Online', 'Online')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    receiver = models.CharField(max_length=100, blank=False, unique=False)
    receiver_Address = models.CharField(
        max_length=1000, blank=False, unique=False)
    receiver_Contact = models.CharField(
        max_length=20, blank=False, unique=False)
    receiver_Email = models.CharField(
        max_length=100, blank=False, unique=False)

    payment = models.CharField(
        max_length=100, choices=payment_types, blank=False)

    service = models.CharField(choices=serviceType,  max_length=100)
    product_Type = models.CharField(choices=productType, max_length=100)
    contents = models.CharField(max_length=100, blank=False, unique=False)
    quantity = models.CharField(max_length=100, blank=False, unique=False)

    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    priority = models.CharField(
        choices=status, blank=True, null=True, max_length=20)
    amount = models.CharField(max_length=100, blank=True, unique=False)
    delivery_Status = models.CharField(
        choices=delivery_StatusType, blank=True, null=True, max_length=50)

    paid = models.BooleanField(default=False)
    reference_id = models.CharField(max_length=100, blank=True, unique=True)

    delivery_now = models.DateField()
    delivery_later = models.DateField(blank=True, null=True)

    pick_up_latitude = models.CharField(blank=True, null=True, max_length=50)
    pick_up_longitude = models.CharField(blank=True, null=True, max_length=50)

    delivery_latitude = models.CharField(blank=True, null=True, max_length=50)
    delivery_longitude = models.CharField(blank=True, null=True, max_length=50)
    otp = models.CharField(max_length=10, blank=True, null=True)

    created = models.DateField()
    cancel_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.receiver
