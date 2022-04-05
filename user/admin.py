from django.contrib import admin
from .models import *

# Register your models here.


admin.site.register(User)
admin.site.register(ReferralModel)
admin.site.register(Ratings)
admin.site.register(Message)
admin.site.register(ReferHistory)
admin.site.register(Notification)


# @admin.register(User)
# class User(admin.ModelAdmin):
#     search_fields = ["username"]

# @admin.register(Message)
# class Message(admin.ModelAdmin):
#     autocomplete_fields = ["receiver"]
