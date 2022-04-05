from django.shortcuts import render
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test

#redirect url
def forbidden(request):
    return render(request,'user/forbidden.html')
REDIRECT_FIELD_NAME = 'forbidden'

#permissions
def has_perm_admin(user):
    return user.is_superuser

def has_perm_a_u_ag_mer_dr(user):
    return not user.is_delivery_man

def has_perm_a_u_ag_mer_dl(user):
    return not user.is_driver

def has_perm_user(user):
    return user.is_user is True

def has_perm_dr_dl(user):
    return user.is_driver or user.is_delivery_man





