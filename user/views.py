from __future__ import division
from typing import Text
from django import http
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from requests.api import request
from rest_framework.serializers import Serializer
from .models import *
from .forms import *
from courier.models import Order
from courier import models
from django.db.models import Q
from courier import views
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from accounting.sslcommerz import unique_trangection_id_generator

from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.generics import ListAPIView
from rest_framework import generics
from .serializers import Notifications, ResponseMSGserializer
# email
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from .tokens import account_activation_token
from django.core.mail import send_mail
from Ecourier.settings import EMAIL_HOST_USER
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_text
from django.contrib.auth import get_user_model
# email ends
from rest_framework import generics
from accounting.models import WalletModel
from django.db.models import Avg
import datetime
from datetime import date
from django.http import JsonResponse, HttpResponse
from accounting.models import ReferPrice
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import json
from .serializers import MessageSerializer, UserSerializer
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum
import random
import string
from django.views.generic.detail import DetailView
# import socket
# socket.getaddrinfo('localhost', 8080)
from courier.models import Order
from courier.forms import OrderForm
from json import dumps
from django.db.models import Count
from .decorators import user_passes_test, REDIRECT_FIELD_NAME, has_perm_admin, has_perm_a_u_ag_mer_dr, \
    has_perm_a_u_ag_mer_dl, has_perm_user, has_perm_dr_dl

# Create your views here.
def email_redirect_view(request):
    return render(request, 'user/wait_for_verification.html')

# registrations here
def register(request):
    form = UserCreation()
    if request.method == 'POST':
        form = UserCreation(request.POST, request.FILES)
        delivery_man = request.POST.get('is_delivery_man')
        driver = request.POST.get('is_driver')
        merchant = request.POST.get('is_merchant')
        agent = request.POST.get('is_agent')

        if delivery_man is not None:
            delivery_man = True
        else:
            delivery_man = False

        if driver is not None:
            driver = True
        else:
            driver = False

        if merchant is not None:
            merchant = True
        else:
            merchant = False

        if agent is not None:
            agent = True
        else:
            agent = False

        if not agent and not merchant and not delivery_man and not driver:
            messages.warning(
                request, 'Please mark a choice from the checkboxes !')
        else:
            if form.is_valid():
                user = form.save(commit=False)
                user.is_active = False
                user.is_delivery_man = delivery_man
                user.is_driver = driver
                user.is_merchant = merchant
                user.is_agent = agent
                user.save()

                current_site = get_current_site(request)
                mail_subject = 'Verify Your Email.'
                message = render_to_string('user/acc_active_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })
                to_email = form.cleaned_data.get('email')
                send_mail(mail_subject, message, EMAIL_HOST_USER, [to_email])
                return render(request, 'user/wait_for_verification.html')
    return render(request, 'registration/register.html', {'form': form})


def user_activation(request, id):
    user = User.objects.get(pk=id)
    if user.is_user:
        user.is_active = True
        user.save()
    else:
        user.is_active = False
        Notification.objects.create(user_id=id, text='Email verified!')
    return redirect('login')


def user_verification(id):
    user = User.objects.get(id=id)
    body = render_to_string(
        'user/verify_email.html', {'data': user})
    send_mail(subject='Email Verification', message=body,
              from_email='djangoapptest@essential-infotech.dev', recipient_list=[user.email], fail_silently=False)


def user_registration(request):
    form = UserCreation()
    if request.method == 'POST':
        form = UserCreation(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.is_user = True
            user.save()
            user_verification(user.id)
            return redirect('email_redirect_view')
    return render(request, 'registration/user_registration.html', {'form': form})


def refer_amount_cal(perm_list, user_id):
    rfr_amount = 0
    count = 0

    refer_list = ['driver', 'delivery man', 'merchant', 'agent', 'user']
    for i in range(0, len(perm_list)):
        if perm_list[i]:
            x = ReferPrice.objects.filter(refer_type=refer_list[i])
            for j in x:
                rfr_amount = j.price
            WalletModel.objects.create(
                user_id=user_id, amount=rfr_amount, tr_method='Refer')
            ReferHistory.objects.create(
                user_id=user_id, type=refer_list[i], amount=rfr_amount)


def register_refer(request, pk):
    form = UserCreation()

    if request.method == 'POST':
        refer_data = get_object_or_404(ReferralModel, pk=pk)
        user_id = refer_data.user.id
        user_activation = False
        form = UserCreation(request.POST, request.FILES)
        delivery_man = request.POST.get('is_delivery_man')
        driver = request.POST.get('is_driver')
        merchant = request.POST.get('is_merchant')
        agent = request.POST.get('is_agent')
        userr = request.POST.get('is_user')
        if delivery_man is not None:
            delivery_man = True
        else:
            delivery_man = False

        if driver is not None:
            driver = True
        else:
            driver = False

        if merchant is not None:
            merchant = True
        else:
            merchant = False

        if agent is not None:
            agent = True
        else:
            agent = False
        if userr:
            userr = True
            user_activation = True
        else:
            userr = False
        perm_list = [driver, delivery_man, merchant, agent, userr]
        if not agent and not merchant and not delivery_man and not driver and not userr:
            messages.warning(
                request, 'Please mark a choice from the checkboxes !')
        else:
            if form.is_valid():
                user = form.save(commit=False)

                user.is_delivery_man = delivery_man
                user.is_driver = driver
                user.is_merchant = merchant
                user.is_agent = agent
                user.is_user = userr
                user.is_active = user_activation
                user.save()
                refer_amount_cal(perm_list, user_id)
                to_email = form.cleaned_data.get('email')
                data = User.objects.get(email=to_email)
                new_id = data.id
                user_verification(new_id)
                refer_data.delete()
                return redirect('email_redirect_view')
    return render(request, 'registration/register_refer.html', {'form': form, 'pk': pk})


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        noti = Notification.objects.filter(user=user, text='Email verified!')
        noti2 = Notification.objects.filter(
            user=user, text='Changed Email!(Verified)')
        if noti:
            noti.update(user=user, text='Changed Email!(Verified)',
                        is_seen=False, is_activated=False)
        elif noti2:
            noti2.update(user=user, text='Changed Email!(Verified)',
                         is_seen=False, is_activated=False)
        else:
            Notification.objects.create(user=user, text='Email verified!')
        user.save()
        return render(request, 'user/verified.html')
    else:
        return HttpResponse('Activation link is invalid!')

# registration ends here

# accounts active and non active parts
@user_passes_test(has_perm_admin, REDIRECT_FIELD_NAME)
def acc_req_list(request):
    id = request.user.id
    non_active = User.objects.filter(is_active=False).order_by('-id')
    count = len(non_active)

    page = request.GET.get('page', 1)
    paginator = Paginator(non_active, 8)
    try:
        non_active = paginator.page(page)
    except PageNotAnInteger:
        non_active = paginator.page(1)
    except EmptyPage:
        non_active = paginator.page(paginator.num_pages)
    context = {
        'non_active': non_active,
        'count': count,
        'id': id,
    }
    return render(request, 'user/inactive_users.html', context)


@user_passes_test(has_perm_admin, REDIRECT_FIELD_NAME)
def acc_approval(request, id):
    url = request.META.get('HTTP_REFERER')
    user = User.objects.get(is_active=False, id=id)
    username = ''
    try:
        user.is_active = True
        user.save()
        username = user.username
        to_mail = user.email
        noti = Notification.objects.filter(
            user=id, is_seen=False, is_activated = False)
        for i in noti:
            i.is_seen = True
            i.is_activated = True
            i.save()
        current_site = get_current_site(request)
        mail_subject = 'Account Approved'
        message = render_to_string('user/account_approved.html', {
            'username': username,
            'domain': current_site.domain,
        })
        send_mail(mail_subject, message, EMAIL_HOST_USER, [to_mail])
    except User.DoesNotExist:
        return HttpResponse('No user Found')
    return HttpResponseRedirect(url)

# accounts active and non active part ends here


def refer_cal(request, pk, ts):
    url = 'http://127.0.0.1:8000/' + str(pk) + '/' + str(ts) + '/'
    try:
        refer_code = ReferralModel.objects.get(code=url)
        pk = refer_code.id
        return redirect('register_refer', pk)
    except:
        return HttpResponse("Refer code Doesn't exits")


def create_refer_link(request):
    userid = request.user.id
    tm = datetime.datetime.now()
    ts = unique_trangection_id_generator()
    x = 'http://127.0.0.1:8000/' + str(request.user.id) + '/' + str(ts) + '/'
    ReferralModel.objects.create(user_id=userid, code=x)
    return JsonResponse(x, safe=False)


# profile
def my_profile(request):
    if request.user.is_authenticated:
        id = request.user.id
        user1 = User.objects.filter(is_delivery_man=True, id=id)
        user2 = User.objects.filter(is_driver=True, id=id)
        user3 = User.objects.filter(is_merchant=True, id=id)
        user4 = User.objects.filter(is_superuser=True, id=id)
        user5 = User.objects.filter(is_agent=True, id=id)
        user6 = User.objects.filter(id=id, is_user=True)
        if user1:
            return redirect('delivery_man_profile', id)
        if user2:
            return redirect('driver_profile', id)
        if user3:
            return redirect('merchant_profile', id)
        if user4:
            return redirect('profiles', id)
        if user5:
            return redirect('agent_profile', id)
        if user6:
            return redirect('user_profile', id)


# visit anyones profile
def profile_visits(request, id):
    user1 = User.objects.filter(is_delivery_man=True, id=id)
    user2 = User.objects.filter(is_driver=True, id=id)
    user3 = User.objects.filter(is_merchant=True, id=id)
    user4 = User.objects.filter(is_superuser=True, id=id)
    user5 = User.objects.filter(is_agent=True, id=id)
    user6 = User.objects.filter(id=id, is_user=True)
    if user1:
        return redirect('delivery_man_profile', id)
    if user2:
        return redirect('driver_profile', id)
    if user3:
        return redirect('merchant_profile', id)
    if user4:
        return redirect('profiles', id)
    if user5:
        return redirect('agent_profile', id)
    if user6:
        return redirect('user_profile', id)


# admin
@user_passes_test(has_perm_admin, REDIRECT_FIELD_NAME)
def profiles(request, id):
    user_list = User.objects.filter(~Q(is_superuser=True))
    length = len(user_list)
    user = User.objects.filter(is_superuser=True, id=id)
    context = {
        'user': user,
        'user_list': user_list,
        'id': id,
        'length': length
    }
    return render(request, 'user/admin_profile.html', context)


@user_passes_test(has_perm_a_u_ag_mer_dr, REDIRECT_FIELD_NAME)
def driver_profile(request, id):
    user_id = request.user.id
    this_month = datetime.datetime.now().month
    this_day = datetime.datetime.today()
    daily_amount = 0

    # monthly
    monthly_order = Order.objects.filter(
        delivery_time__month=this_month, driver=id)
    dv_sc = Order.objects.filter(
        driver=id, delivery_Status='Complete', delivery_time__month=this_month).count()
    dv_ing = Order.objects.filter(
        driver=id, delivery_Status='Delivering', created__month=this_month).count()
    dv_pn = Order.objects.filter(
        driver=id, delivery_Status='Pending', created__month=this_month).count()

    # daily
    daily_deliveries = Order.objects.filter(
        delivery_time=this_day, driver=id)
    daily_dv_sc = Order.objects.filter(
        driver=id, delivery_Status='Complete', delivery_time=this_day).count()
    daily_dv_ing = Order.objects.filter(
        driver=id, delivery_Status='Delivering', created=this_day).count()
    daily_dv_pn = Order.objects.filter(
        driver=id, delivery_Status='Pending', created=this_day).count()
    daily_amount_received = Order.objects.filter(
        driver=id, delivery_Status='Complete', delivery_time=this_day).values(
            'amount').aggregate(Sum('amount'))
    for key, value in daily_amount_received.items():
        if value:
            daily_amount = value

    user = User.objects.filter(is_driver=True, id=id)
    ratings = Ratings.objects.filter(rated_user=id)
    context = {
        'user': user,
        'ratings': ratings,
        'monthly_order': monthly_order,
        'complete_count': dv_sc,
        'pending_count': dv_pn,
        'delivering_count': dv_ing,
        'daily_deliveries': daily_deliveries,
        'daily_dv_sc': daily_dv_sc,
        'daily_dv_ing': daily_dv_ing,
        'daily_dv_pn': daily_dv_pn,
        'daily_amount': daily_amount,
        'id': id,
    }
    return render(request, 'user/driver_profile.html', context)


def merchant_profile(request, id):
    if request.user.is_merchant or request.user.is_superuser:
        recent_del = Order.objects.filter(user=id).order_by('-id')[:5]
        this_month = datetime.datetime.now().month
        delivery = Order.objects.filter(user=id, created__month=this_month)
        complete_count = 0
        pending_count = 0
        delivering_count = 0
        status = ''
        for i in delivery:
            status = i.delivery_Status
            if status == 'Complete':
                complete_count += 1

            if status == 'Pending':
                pending_count += 1

            if status == 'Delivering':
                delivering_count += 1

        user = User.objects.filter(is_merchant=True, id=id)
        user_list = User.objects.filter(
            Q(is_delivery_man=True) | Q(is_driver=True))
        context = {
            'recent_del': recent_del,
            'complete_count': complete_count,
            'pending_count': pending_count,
            'delivering_count': delivering_count,
            'user': user,
            'user_list': user_list,
            'id': id,
        }
        return render(request, 'user/merchant_profile.html', context)
    else:
        return redirect('forbidden')


def agent_profile(request, id):
    if request.user.is_agent or request.user.is_superuser:
        recent_del = Order.objects.filter(user=id).order_by('-id')[:5]
        this_month = datetime.datetime.now().month
        delivery = Order.objects.filter(user=id, created__month=this_month)

        complete_count = 0
        pending_count = 0
        delivering_count = 0
        status = ''
        for i in delivery:
            status = i.delivery_Status
            if status == 'Complete':
                complete_count += 1

            if status == 'Pending':
                pending_count += 1

            if status == 'Delivering':
                delivering_count += 1

        user = User.objects.filter(is_agent=True, id=id)
        user_list = User.objects.filter(
            Q(is_delivery_man=True) | Q(is_driver=True))
        context = {
            'recent_del': recent_del,
            'complete_count': complete_count,
            'pending_count': pending_count,
            'delivering_count': delivering_count,
            'user': user,
            'user_list': user_list,
            'id': id,
        }
        return render(request, 'user/agent_profile.html', context)
    else:
        return redirect('forbidden')


# need fixing(no data for him in order table)
@user_passes_test(has_perm_a_u_ag_mer_dl, REDIRECT_FIELD_NAME)
def delivery_man_profile(request, id):
    month = datetime.datetime.now().month
    recent_del = Order.objects.filter(driver=id).order_by('-id')[:10]
    delivery = Order.objects.filter(driver=id, created__month=month)
    complete_count = 0
    pending_count = 0
    delivering_count = 0
    status = ''
    for i in delivery:
        status = i.delivery_Status

        if status == 'Complete':
            complete_count += 1

        if status == 'Pending':
            pending_count += 1

        if status == 'Delivering':
            delivering_count += 1

    ratings = Ratings.objects.filter(rated_user=id)
    user = User.objects.filter(is_delivery_man=True, id=id)
    context = {
        'recent_del': recent_del,
        'complete_count': complete_count,
        'pending_count': pending_count,
        'delivering_count': delivering_count,
        'user': user,
        'ratings': ratings,
        'id': id,
    }
    return render(request, 'user/delivery_man_profile.html', context)


def user_profile(request, id):
    if request.user.is_user or request.user.is_superuser:
        recent_del = Order.objects.filter(user=id).order_by('-id')[:5]
        this_month = datetime.datetime.now().month
        delivery = Order.objects.filter(user=id, created__month=this_month)

        complete_count = 0
        pending_count = 0
        delivering_count = 0
        status = ''
        for i in delivery:
            status = i.delivery_Status

            if status == 'Complete':
                complete_count += 1

            if status == 'Pending':
                pending_count += 1

            if status == 'Delivering':
                delivering_count += 1

        user_list = User.objects.filter(
            Q(is_delivery_man=True) | Q(is_driver=True))

        user = User.objects.filter(id=id)
        context = {
            'user_list': user_list,
            'user': user,
            'recent_del': recent_del,
            'complete_count': complete_count,
            'pending_count': pending_count,
            'delivering_count': delivering_count,
            'id': id
        }
        return render(request, 'user/user_profile.html', context)
    else:
        return redirect('forbidden')


def edit_profile_admin(request, id):
    if request.user.is_superuser:
        user_data = User.objects.filter(id=id)
        user = User.objects.get(id=id)
        form = Admin_Profile_Edit(instance=user)
        if request.method == 'POST':
            form = Admin_Profile_Edit(
                request.POST, request.FILES, instance=user)
            if form.is_valid():
                form.save()
            return redirect('profiles', id)
        context = {
            'form': form,
            'user_data': user_data,
            'id': id,
        }
        return render(request, 'user/edit_profile_admin.html', context)
    else:
        return redirect('forbidden')


def edit_profile_driver(request, id):
    if request.user.is_driver:
        user_data = User.objects.filter(id=id)
        user = User.objects.get(id=id)
        form = Driver_profile_Edit(instance=user)
        if request.method == 'POST':
            form = Driver_profile_Edit(
                request.POST, request.FILES, instance=user)
            if form.is_valid():
                form.save()
            return redirect('driver_profile', id)
        context = {
            'form': form,
            'user_data': user_data,
            'id': id,
        }
        return render(request, 'user/edit_profile_driver.html', context)
    else:
        return redirect('forbidden')


def edit_profile_delivery_man(request, id):
    if request.user.is_delivery_man:
        user_data = User.objects.filter(id=id)
        user = User.objects.get(id=id)
        form = Delivery_man_profile_Edit(instance=user)
        if request.method == 'POST':
            form = Delivery_man_profile_Edit(
                request.POST, request.FILES, instance=user)
            if form.is_valid():
                form.save()
            return redirect('delivery_man_profile', id)
        context = {
            'form': form,
            'user_data': user_data,
            'id': id,
        }
        return render(request, 'user/edit_profile_delivery_man.html', context)
    else:
        return redirect('forbidden')


def edit_profile_merchant(request, id):
    if request.user.is_merchant:
        user_data = User.objects.filter(id=id)
        user = User.objects.get(id=id)
        form = Merchant_profile_Edit(instance=user)
        if request.method == 'POST':
            form = Merchant_profile_Edit(
                request.POST, request.FILES, instance=user)
            if form.is_valid():
                form.save()
            return redirect('merchant_profile', id)
        context = {
            'form': form,
            'user_data': user_data,
            'id': id,
        }
        return render(request, 'user/edit_profile_merchant.html', context)
    else:
        return redirect('forbidden')


def edit_profile_agent(request, id):
    if request.user.is_agent:
        user_data = User.objects.filter(id=id)
        user = User.objects.get(id=id)
        form = Agent_profile_Edit(instance=user)
        if request.method == 'POST':
            form = Agent_profile_Edit(
                request.POST, request.FILES, instance=user)
            if form.is_valid():
                form.save()
            return redirect('agent_profile', id)
        context = {
            'form': form,
            'user_data': user_data,
            'id': id,
        }
        return render(request, 'user/edit_agent_profile.html', context)
    else:
        return redirect('forbidden')


def edit_profile_user(request, id):
    if request.user.is_user:
        user_data = User.objects.filter(id=id)
        user = User.objects.get(id=id)
        form = User_profile_Edit(instance=user)
        if request.method == 'POST':
            form = User_profile_Edit(
                request.POST, request.FILES, instance=user)
            if form.is_valid():
                form.save()
            return redirect('user_profile', id)
        context = {
            'form': form,
            'user_data': user_data,
            'id': id,
        }
        return render(request, 'user/edit_profile_user.html', context)
    else:
        return redirect('forbidden')

@user_passes_test(has_perm_dr_dl, REDIRECT_FIELD_NAME)
def available(request, id):
    data = User.objects.get(id=id)
    url = request.META.get('HTTP_REFERER')
    if data.is_available is True:
        data.is_available = False
    else:
        data.is_available = True
    data.save()
    return HttpResponseRedirect(url)
# profile ends here

# vehicles
def vehicle_settings(request, id):
    if request.user.is_driver:
        user_data = User.objects.filter(id=id)
        user = User.objects.get(id=id)
        form = DriverVehicle(instance=user)
        if request.method == 'POST':
            form = DriverVehicle(request.POST, request.FILES, instance=user)
            if form.is_valid():
                form.save()
                return redirect('profile_visits', id)
        context = {
            'form': form,
            'user_data': user_data,
            'id': id,
        }
        return render(request, 'user/manage_vehicle.html', context)
    else:
        return redirect('forbidden')


# change_password nott forget pass
def change_password(request):
    id = request.user.id
    user = User.objects.filter(id=id)
    form = PasswordChangeForm(request.user)
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('logout')
    return render(request, 'user/change_pass.html', {'form': form, 'user': user, 'id': id})


# star ratings
def rate_user(request):
    if request.method == 'POST':
        el_id = request.POST.get('el_id')
        val = request.POST.get('val')

        obj = Ratings.objects.get(id=el_id)

        storing_prev_rated_number = obj.rated_number
        obj.rated_number = val

        obj.count = obj.count + 1
        store_count = obj.count

        old_addition_values = obj.storing_prev_now_rated_value
        obj.storing_prev_now_rated_value = float(
            old_addition_values) + float(val)

        store_storing_prev_now_rated_value = obj.storing_prev_now_rated_value

        obj.avg_rating = float(
            store_storing_prev_now_rated_value / store_count)
        obj.avg_rating = format(obj.avg_rating, ".1f")
        obj.rating_giver = request.user
        obj.save()
        return JsonResponse({'success': 'true', 'rated_number': val}, safe=False)
    return JsonResponse({'success': 'false'})


@user_passes_test(has_perm_admin, REDIRECT_FIELD_NAME)
def user_ratings(request):
    id = request.user.id
    ratings = Ratings.objects.all()
    return render(request, 'user/ratings.html', {'ratings': ratings, 'id': id})


def user_msg(request, id):
    user_id = request.user.id
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        msg = request.POST.get('msg')
        Message.objects.create(sender_id=user_id, receiver_id=id, msg=msg)
        return HttpResponseRedirect(url)


def complain_box(request, id):
    if not request.user.is_superuser:
        url = request.META.get('HTTP_REFERER')
        user_id = request.user.id
        if request.method == 'POST':
            user = User.objects.filter(is_superuser=True)
            admin_id = ''
            msg = request.POST.get('msg')
            try:
                if msg:
                    for i in user:
                        admin_id = i.id
                        Message.objects.create(
                            sender_id=user_id, receiver_id=admin_id, msg=msg)
            except:
                return HttpResponse('Something Went Wrong')
            return HttpResponseRedirect(url)
    else:
        return HttpResponse('You are an admin and you can not message yourself! This option is intended to get messages from users.Only users can send messages from here(To Admins)')

# real time posting with js


def get_complains(request):
    if request.user.is_superuser:
        url = request.META.get('HTTP_REFERER')
        my_id = request.user.id
        my_msg = Message.objects.filter(receiver=my_id, mark_as_read=True)
        form = AdminMessage()
        if request.method == 'POST':
            form = AdminMessage(request.POST)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.sender = request.user
                instance.save()
                return HttpResponseRedirect(url)
        return render(request, 'user/complains.html', {'my_msg': my_msg, 'form': form})
    else:
        return redirect('forbidden')


def mark_as_read(request, id):
    url = request.META.get('HTTP_REFERER')
    obj = Message.objects.filter(id=id)
    for i in obj:
        i.mark_as_read = True
        i.save()
    return HttpResponseRedirect(url)


class Get_complains(APIView):
    # serializer_class = MessageSerializer
    def get(self, request, format=None):
        msg = Message.objects.filter(
            receiver_id=request.user.id, mark_as_read=False).order_by('-sent')
        data = []
        for i in msg:
            json = {
                'Sender': i.sender.username,
                'Sender_ID': i.sender.id,
                'MID': i.id,
                'Msg': i.msg,
                'Receiver': i.receiver.username,
                'Sent': i.sent,
                'Read': i.mark_as_read,
            }
            data.append(json)
        return Response(data)


def delete_complains(request, id):
    url = request.META.get('HTTP_REFERER')
    obj = get_object_or_404(Message, id=id)
    obj.delete()
    return HttpResponseRedirect(url)


def search_user(request):
    query = request.GET.get("q")
    context = {}
    if query:
        users = User.objects.filter(
            Q(username__istartswith=query, is_active=False))
        if users:
            page = request.GET.get('page', 1)
            paginator = Paginator(users, 10)
            try:
                users = paginator.page(page)
            except PageNotAnInteger:
                users = paginator.page(1)
            except EmptyPage:
                users = paginator.page(paginator.num_pages)
            context = {'users': users}
            return render(request, 'user/search.html', context)
        else:
            messages.warning(request,
                             'User matching query does not exist and also You can only search for unapproved users')
            return redirect('acc_req_list')


def search_user2(request):
    query = request.GET.get("q2")
    context = {}
    if query:
        users = Ratings.objects.filter(Q(rated_user__username__istartswith=query, rated_user__is_delivery_man=True) | Q(
            rated_user__username__istartswith=query, rated_user__is_driver=True))
        if users:
            page = request.GET.get('page', 1)
            paginator = Paginator(users, 10)
            try:
                users = paginator.page(page)
            except PageNotAnInteger:
                users = paginator.page(1)
            except EmptyPage:
                users = paginator.page(paginator.num_pages)
            context = {'users': users}
            return render(request, 'user/search2.html', context)
        else:
            messages.warning(
                request, 'User matching query does not exist and you can only search for deliveryman/driver.')
            return redirect('user_ratings')


def search_user3(request):
    query = request.GET.get('q3')
    context = {}
    if query:
        users = User.objects.filter(username__istartswith=query)
        if users:
            page = request.GET.get('page', 1)
            paginator = Paginator(users, 10)
            try:
                users = paginator.page(page)
            except PageNotAnInteger:
                users = paginator.page(1)
            except EmptyPage:
                users = paginator.page(paginator.num_pages)
            context = {
                'users': users,
            }
            return render(request, 'user/search3.html', context)
        else:
            id = request.user.id
            messages.warning(request, 'No User Found.')
            return redirect('profile_visits', id)


def search_user4(request):
    query = request.GET.get('q4')
    context = {}
    if query:
        users = User.objects.filter(
            username__istartswith=query).order_by('-id')
        if users:
            page = request.GET.get('page', 1)
            paginator = Paginator(users, 10)
            try:
                users = paginator.page(page)
            except PageNotAnInteger:
                users = paginator.page(1)
            except EmptyPage:
                users = paginator.page(paginator.num_pages)
            context = {
                'users': users,
            }
            return render(request, 'user/search4.html', context)
        else:
            messages.warning(request, 'No User Found.')
            return redirect('users')


def search_agents(request):
    query = request.GET.get('q5')
    context = {}
    if query:
        agents = User.objects.filter(
            username__istartswith=query, is_agent=True, is_active=True).order_by('-id')
        if agents:
            page = request.GET.get('page', 1)
            paginator = Paginator(agents, 10)
            try:
                agents = paginator.page(page)
            except PageNotAnInteger:
                agents = paginator.page(1)
            except EmptyPage:
                agents = paginator.page(paginator.num_pages)
            context = {
                'agents': agents,
            }
            return render(request, 'user/search_agents.html', context)
        else:
            messages.warning(request, 'No active agent found with this name')
            return redirect('agent_list')


def search_drivers(request):
    query = request.GET.get('q6')
    context = {}
    if query:
        drivers = User.objects.filter(
            username__istartswith=query, is_driver=True, is_active=True).order_by('-id')
        if drivers:
            page = request.GET.get('page', 1)
            paginator = Paginator(drivers, 10)
            try:
                drivers = paginator.page(page)
            except PageNotAnInteger:
                drivers = paginator.page(1)
            except EmptyPage:
                drivers = paginator.page(paginator.num_pages)
            context = {
                'drivers': drivers,
            }
            return render(request, 'user/search_drivers.html', context)
        else:
            messages.warning(request, 'No active driver found with this name')
            return redirect('driver_ratings')


@user_passes_test(has_perm_admin, REDIRECT_FIELD_NAME)
def users(request):
    users = User.objects.filter(~Q(is_superuser = True),is_active = True)
    user_list = User.objects.filter(is_user = True, is_active = True)
    agent_list = User.objects.filter(is_agent = True, is_active = True)
    merchant_list = User.objects.filter(is_merchant = True, is_active = True)
    driver_list = User.objects.filter(is_driver = True, is_active = True)
    delivery_man_list = User.objects.filter(is_delivery_man = True, is_active = True)
    count = len(users)

    context = {
        'user_list': user_list,
        'agent_list': agent_list,
        'merchant_list': merchant_list,
        'driver_list': driver_list,
        'delivery_man_list': delivery_man_list,
        'count': count,
    }
    return render(request, 'user/user_list.html', context)


@api_view(['GET'])
def user_list_view(request):
    user_id = request.user.id
    user = User.objects.filter(~Q(id=user_id))
    serialize = UserSerializer(user, many=True)
    return Response(serialize.data)


def monthly_order_bar_chart(request):
    labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Octo', 'Nov', 'Dec']
    data = []
    queryset = Order.objects.all()
    jan = 0
    feb = 0
    mar = 0
    apr = 0
    may = 0
    jun = 0
    jul = 0
    aug = 0
    sep = 0
    octo = 0
    nov = 0
    dec = 0
    year = datetime.datetime.now().year

    for i in range(1, 13):
        if i == 1:
            jan = Order.objects.filter(
                created__month = i, created__year = year).count()
            data.append(jan)
        if i == 2:
            feb = Order.objects.filter(
                created__month=i, created__year=year).count()
            data.append(feb)
        if i == 3:
            mar = Order.objects.filter(
                created__month=i, created__year=year).count()
            data.append(mar)
        if i == 4:
            apr = Order.objects.filter(
                created__month=i, created__year=year).count()
            data.append(apr)
        if i == 5:
            may = Order.objects.filter(
                created__month=i, created__year=year).count()
            data.append(may)
        if i == 6:
            jun = Order.objects.filter(
                created__month=i, created__year=year).count()
            data.append(jun)
        if i == 7:
            jul = Order.objects.filter(
                created__month=i, created__year=year).count()
            data.append(jul)
        if i == 8:
            aug = Order.objects.filter(
                created__month=i, created__year=year).count()
            data.append(aug)
        if i == 9:
            sep = Order.objects.filter(
                created__month=i, created__year=year).count()
            data.append(sep)
        if i == 10:
            octo = Order.objects.filter(
                created__month=i, created__year=year).count()
            data.append(octo)
        if i == 11:
            nov = Order.objects.filter(
                created__month=i, created__year=year).count()
            data.append(nov)
        if i == 12:
            dec = Order.objects.filter(
                created__month=i, created__year=year).count()
            data.append(dec)

    return JsonResponse(data={
        'labels': labels,
        'data': data,
    })


def cal(data):
    diff = ''
    month = datetime.datetime.now().month
    for j in range(0, 12):
        if month == j+1:
            if data[j] >= data[j-1]:
                diff = str(data[j] - data[j-1]) + \
                    ' more orders than last month'
            elif data[j] < data[j-1]:
                diff = str(data[j-1] - data[j]) + \
                    ' less orders than last month'
    return diff


class Comparing_monthly_diff(APIView):
    def get(self, request, format=None):
        data = []
        jan = 0
        feb = 0
        mar = 0
        apr = 0
        may = 0
        jun = 0
        jul = 0
        aug = 0
        sep = 0
        octo = 0
        nov = 0
        dec = 0
        year = datetime.datetime.now().year

        for i in range(1, 13):
            if i == 1:
                jan = Order.objects.filter(
                    created__month=i, created__year=year).count()
                data.append(jan)
            if i == 2:
                feb = Order.objects.filter(
                    created__month=i, created__year=year).count()
                data.append(feb)
            if i == 3:
                mar = Order.objects.filter(
                    created__month=i, created__year=year).count()
                data.append(mar)
            if i == 4:
                apr = Order.objects.filter(
                    created__month=i, created__year=year).count()
                data.append(apr)
            if i == 5:
                may = Order.objects.filter(
                    created__month=i, created__year=year).count()
                data.append(may)
            if i == 6:
                jun = Order.objects.filter(
                    created__month=i, created__year=year).count()
                data.append(jun)
            if i == 7:
                jul = Order.objects.filter(
                    created__month=i, created__year=year).count()
                data.append(jul)
            if i == 8:
                aug = Order.objects.filter(
                    created__month=i, created__year=year).count()
                data.append(aug)
            if i == 9:
                sep = Order.objects.filter(
                    created__month=i, created__year=year).count()
                data.append(sep)
            if i == 10:
                octo = Order.objects.filter(
                    created__month=i, created__year=year).count()
                data.append(octo)
            if i == 11:
                nov = Order.objects.filter(
                    created__month=i, created__year=year).count()
                data.append(nov)
            if i == 12:
                dec = Order.objects.filter(
                    created__month=i, created__year=year).count()
                data.append(dec)

        diff = cal(data)
        return Response(diff)


def validate_username(request):
    username = request.GET.get('username', None)
    data = {
        'is_taken': User.objects.filter(username__iexact=username).exists()
    }
    return JsonResponse(data)


class User_notification(LoginRequiredMixin, generics.ListAPIView):
    serializer_class = Notifications
    def get_queryset(self):
        return Notification.objects.filter(is_seen = False, is_activated = False)
       

def create_unique_id(size=12, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def change_email(request):
    if not request.user.is_authenticated:
        return redirect('login')
    my_id = request.user.id
    user = User.objects.get(id=my_id)
    user_mail = User.objects.filter(id=my_id)
    for i in user_mail:
        mail = i.email
    form = EmailChangeForm(instance=user)
    if request.method == 'POST':
        form = EmailChangeForm(request.POST, instance=user)
        if not request.user.is_superuser:
            if form.is_valid():
                user = form.save(commit=False)
                user.is_active = False
                user.save()
                current_site = get_current_site(request)
                mail_subject = 'Verify Your Email.'
                message = render_to_string('user/acc_active_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })
                to_email = form.cleaned_data.get('email')
                send_mail(mail_subject, message, EMAIL_HOST_USER, [to_email])
                return render(request, 'user/verify_ur_email.html')
        else:
            if form.is_valid():
                user = form.save(commit=False)
                user.save()
    return render(request, 'user/change_email.html', {'form': form})


# checking for same email
def get_email(request):
    email = request.GET.get('email', None)
    data = {
        'is_taken': User.objects.filter(email__iexact=email).exists(),
    }
    return JsonResponse(data)


class Email_update(APIView):
    def get(self, request, format=None):
        updating_email = User.objects.filter(id=request.user.id)
        data = []
        for i in updating_email:
            d = {'email':  i.email}
            data.append(d)
        return Response(data)


# auto suggests name while searching
def autosuggest(request):
    query_original = request.GET.get('term')
    queryset = User.objects.filter(username__startswith=query_original)
    if queryset:
        mylist = []
        mylist += [x.username for x in queryset]
    else:
        mylist = ['No matches found']
    return JsonResponse(mylist, safe=False)


def delivery_status_admin_profile(request):
    pending = Order.objects.filter(delivery_Status='Pending').count()
    delivering = Order.objects.filter(delivery_Status='Delivering').count()
    complete = Order.objects.filter(delivery_Status='Complete').count()
    returned = Order.objects.filter(delivery_Status='Return').count()
    data = []
    for i in range(0, 1):
        d = {
            'pending': pending,
            'delivering': delivering,
            'complete': complete,
            'returned': returned,
        }
        data.append(d)
    return JsonResponse(data, safe=False)


@user_passes_test(has_perm_admin, REDIRECT_FIELD_NAME)
def agent_list(request):
    agents = User.objects.filter(is_agent=True, is_active=True)
    agent_count = len(agents)
    page = request.GET.get('page', 1)
    paginator = Paginator(agents, 10)
    try:
        agents = paginator.page(page)
    except PageNotAnInteger:
        agents = paginator.page(1)
    except EmptyPage:
        agents = paginator.page(paginator.num_pages)
    context = {
        'agents': agents,
        'agent_count': agent_count
    }
    return render(request, 'user/agent_list.html', context)


def return_deliveries(request):
    returned_c = 0
    returning = Order.objects.filter(
        delivery_Status='Return', user__is_agent=True)
    return_len = len(returning)
    returning_cash = Order.objects.filter(delivery_Status='Return', user__is_agent=True).values(
        'amount').aggregate(Sum('amount'))
    for k, v in returning_cash.items():
        if v:
            returned_c = v
    context = {
        'returned': returning,
        'returned_c': returned_c,
        'return_len': return_len,
    }
    return render(request, 'user/agent_returned_deliveries.html', context)


def delivering_deliveries(request):
    delivering_c = 0
    deliveries = Order.objects.filter(
        delivery_Status='Delivering', user__is_agent=True)
    delivering_len = len(deliveries)
    delivering_cash = Order.objects.filter(delivery_Status='Delivering', user__is_agent=True).values(
        'amount').aggregate(Sum('amount'))
    for k, v in delivering_cash.items():
        if v:
            delivering_c = v
    context = {
        'delivering': deliveries,
        'delivering_c': delivering_c,
        'delivering_len': delivering_len,
    }
    return render(request, 'user/agent_delivering_deliveries.html', context)


def pending_deliveries(request):
    pending_c = 0
    pending_deliveries = Order.objects.filter(
        delivery_Status='Pending', user__is_agent=True)
    pending_len = len(pending_deliveries)
    pending_cash = Order.objects.filter(delivery_Status='Pending', user__is_agent=True).values(
        'amount').aggregate(Sum('amount'))
    for k, v in pending_cash.items():
        if v:
            pending_c = v

    context = {
        'pending': pending_deliveries,
        'pending_c': pending_c,
        'pending_len': pending_len,
    }
    return render(request, 'user/agent_pending_deliveries.html', context)


def complete_deliveries(request):
    complete_c = 0
    complete_deliveries = Order.objects.filter(
        delivery_Status='Complete', user__is_agent=True)
    complete_len = len(complete_deliveries)
    complete_cash = Order.objects.filter(delivery_Status='Complete', user__is_agent=True).values(
        'amount').aggregate(Sum('amount'))
    for k, v in complete_cash.items():
        if v:
            complete_c = v

    context = {
        'complete': complete_deliveries,
        'complete_c': complete_c,
        'complete_len': complete_len,
    }
    return render(request, 'user/agent_complete_deliveries.html', context)


def agent_stats_dashboard(request):
    data = []
    month = datetime.datetime.now().month
    year = datetime.datetime.now().year
    all_orders = Order.objects.filter(user__is_agent=True, delivery_Status="Complete", delivery_time__month=month,
                                      delivery_time__year=year)

    total_cash_agent = Order.objects.filter(user__is_agent=True, delivery_Status="Complete", delivery_time__month=month,
                                            delivery_time__year=year).values('amount').aggregate(Sum('amount'))

    for entry in all_orders:
        preload = {
            'username': entry.user.username,
            'uid': entry.user.id,
            'status': entry.delivery_Status,
            'amount': entry.amount,
            'reffer_id': entry.reference_id,
            'driver': entry.driver.username,
            'driverid': entry.driver.id,
            'orderid': entry.id,
        }
        data.append(preload)
    return JsonResponse(data, safe=False)


def delete_agent_stat(request, id):
    url = request.META.get('HTTP_REFERER')
    obj = get_object_or_404(Order, id=id)
    obj.delete()
    return HttpResponseRedirect(url)


def agents_order_detail(request, id):
    month = datetime.datetime.now().month
    year = datetime.datetime.now().year
    orders = Order.objects.filter(id=id, user__is_agent=True, delivery_Status="Complete", delivery_time__month=month,
                                  delivery_time__year=year)
    context = {
        'orders': orders,
        'id': id,
    }
    return render(request, 'user/order_detail_agent.html', context)


@user_passes_test(has_perm_admin, REDIRECT_FIELD_NAME)
def driver_ratings(request):
    drivers_count = User.objects.filter(is_driver=True, is_active=True).count()
    ratings = Ratings.objects.filter(
        rated_user__is_driver=True, rated_user__is_active=True)
    page = request.GET.get('page', 1)
    paginator = Paginator(ratings, 12)
    try:
        ratings = paginator.page(page)
    except PageNotAnInteger:
        ratings = paginator.page(1)
    except EmptyPage:
        ratings = paginator.page(paginator.num_pages)
    return render(request, 'user/driver_ratings.html', {'ratings': ratings, 'drivers_count': drivers_count})


# driver list for reviews/locations
@user_passes_test(has_perm_admin, REDIRECT_FIELD_NAME)
def drivers_detail(request):
    users = User.objects.filter(is_driver=True, is_active=True)
    return render(request, 'user/drivers_detail.html', {'users': users})


@user_passes_test(has_perm_admin, REDIRECT_FIELD_NAME)
def driver_management(request, id):
    location = User.objects.get(id=id)
    latitude = dumps(location.latitude)
    longitude = dumps(location.longitude)

    month = datetime.datetime.now().month
    year = datetime.datetime.now().year

    success = Order.objects.filter(driver_id=id, delivery_time__month=month,
                                   delivery_time__year=year, delivery_Status="Complete").count()

    delivering = Order.objects.filter(driver_id=id, delivery_time__month=month,
                                      delivery_time__year=year, delivery_Status="Delivering").count()

    pending = Order.objects.filter(driver_id=id, delivery_time__month=month,
                                   delivery_time__year=year, delivery_Status="Pending").count()

    returned = Order.objects.filter(driver_id=id, delivery_time__month=month,
                                    delivery_time__year=year, delivery_Status="Return").count()

    queryset = User.objects.filter(id=id)

    review_msg = Message.objects.filter(receiver_id=id)
    context = {
        'latitude': latitude,
        'longitude': longitude,

        'success': success,
        'delivering': delivering,
        'pending': pending,
        'returned': returned,
        'review_msg': review_msg,
        'queryset': queryset,
        'id': id,
    }
    return render(request, 'user/driver_management.html', context)


class MoneyTransferAPI(LoginRequiredMixin, ListAPIView):
    serializer_class = Notifications

    def get_queryset(self):
        queryset = Notification.objects.all()
        user_id = self.request.user.id
        if user_id:
            queryset = queryset.filter(user=user_id, is_transfer=True)
            return queryset


class MyCommissionAPI(LoginRequiredMixin, ListAPIView):
    serializer_class = Notifications

    def get_queryset(self):
        queryset = Notification.objects.all()
        user_id = self.request.user.id
        if self.request.user.is_driver or self.request.user.is_delivery_man:
            queryset = queryset.filter(user=user_id, is_manged=True)
            return queryset


class PaymentNotificationAPI(LoginRequiredMixin, ListAPIView):
    serializer_class = Notifications

    def get_queryset(self):
        if self.request.user.is_superuser:
            queryset = Notification.objects.all()
            queryset = queryset.filter(is_payment=True, is_seen=False)
            return queryset


def inactive_message(request):
    username = request.GET.get('username', None)
    data = {
        'is_inactive': User.objects.filter(username__iexact = username, is_active = False).exists(),
    }
    return JsonResponse(data)


def demo_animation(request):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        text = request.POST.get('text')
        email = request.POST.get('email')
        mail_subject = 'Customer Email Queries'
        to_email = EMAIL_HOST_USER
        message = render_to_string('user/user_query.html', {
            'text': text,
        })
        send_mail(mail_subject, message, email, [to_email])
        if send_mail:
            print('Mail was sent')
        return HttpResponseRedirect(url)
    return render(request,'user/particle.html')


@user_passes_test(has_perm_user, REDIRECT_FIELD_NAME)
def user_dashboard(request):
    this_month = datetime.datetime.now().month
    this_year = datetime.datetime.now().year
    this_year_orders = Order.objects.filter(user_id = request.user.id, delivery_time__year = this_year).count()

    complete_orders = Order.objects.filter(user_id = request.user.id, delivery_Status = 'Complete',
     delivery_time__month = this_month, delivery_time__year = this_year).count()

    delivering_orders = Order.objects.filter(user_id = request.user.id, delivery_Status = 'Delivering',
     created__month = this_month, created__year = this_year).count()

    orders = Order.objects.filter(user_id = request.user.id, delivery_time__year = this_year)

    context = {
        'complete_orders': complete_orders,
        'delivering_orders': delivering_orders,

        'orders': orders,
        'this_year_orders': this_year_orders
    }
    return render(request,'dashboards/user_dashboard.html', context)


@user_passes_test(has_perm_user, REDIRECT_FIELD_NAME)
def individual_order_chart_for_user(request):
    labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Octo', 'Nov', 'Dec']
    data = []
    jan = 0
    feb = 0
    mar = 0
    apr = 0
    may = 0
    jun = 0
    jul = 0
    aug = 0
    sep = 0
    octo = 0
    nov = 0
    dec = 0
    year = datetime.datetime.now().year
    for i in range(1, 13):
        if i == 1:
            jan = Order.objects.filter(user_id = request.user.id,
                created__month=i, created__year=year).count()
            data.append(jan)
        if i == 2:
            feb = Order.objects.filter(user_id = request.user.id,
                created__month=i, created__year=year).count()
            data.append(feb)
        if i == 3:
            mar = Order.objects.filter(user_id = request.user.id,
                created__month=i, created__year=year).count()
            data.append(mar)
        if i == 4:
            apr = Order.objects.filter(user_id = request.user.id,
                created__month=i, created__year=year).count()
            data.append(apr)
        if i == 5:
            may = Order.objects.filter(user_id = request.user.id,
                created__month=i, created__year=year).count()
            data.append(may)
        if i == 6:
            jun = Order.objects.filter(user_id = request.user.id,
                created__month=i, created__year=year).count()
            data.append(jun)
        if i == 7:
            jul = Order.objects.filter(user_id = request.user.id,
                created__month=i, created__year=year).count()
            data.append(jul)
        if i == 8:
            aug = Order.objects.filter(user_id = request.user.id,
                created__month=i, created__year=year).count()
            data.append(aug)
        if i == 9:
            sep = Order.objects.filter(user_id = request.user.id,
                created__month=i, created__year=year).count()
            data.append(sep)
        if i == 10:
            octo = Order.objects.filter(user_id = request.user.id,
                created__month=i, created__year=year).count()
            data.append(octo)
        if i == 11:
            nov = Order.objects.filter(user_id = request.user.id,
                created__month=i, created__year=year).count()
            data.append(nov)
        if i == 12:
            dec = Order.objects.filter(user_id = request.user.id,
                created__month=i, created__year=year).count()
            data.append(dec)

    return JsonResponse(data={
        'labels': labels,
        'data': data,
    })


@user_passes_test(has_perm_user, REDIRECT_FIELD_NAME)
def individual_order_completed_user(request):
    labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Octo', 'Nov', 'Dec']
    data = []
    jan = 0
    feb = 0
    mar = 0
    apr = 0
    may = 0
    jun = 0
    jul = 0
    aug = 0
    sep = 0
    octo = 0
    nov = 0
    dec = 0
    year = datetime.datetime.now().year
    for i in range(1, 13):
        if i == 1:
            jan = Order.objects.filter(user_id = request.user.id,
                delivery_time__month = i, delivery_time__year = year , delivery_Status = 'Return').count()
            data.append(jan)
        if i == 2:
            feb = Order.objects.filter(user_id = request.user.id,
                delivery_time__month = i, delivery_time__year = year , delivery_Status = 'Return').count()
            data.append(feb)
        if i == 3:
            mar = Order.objects.filter(user_id = request.user.id,
                delivery_time__month = i, delivery_time__year = year , delivery_Status = 'Return').count()
            data.append(mar)
        if i == 4:
            apr = Order.objects.filter(user_id = request.user.id,
                delivery_time__month = i, delivery_time__year = year , delivery_Status = 'Return').count()
            data.append(apr)
        if i == 5:
            may = Order.objects.filter(user_id = request.user.id,
                delivery_time__month = i, delivery_time__year = year , delivery_Status = 'Return').count()
            data.append(may)
        if i == 6:
            jun = Order.objects.filter(user_id = request.user.id,
                delivery_time__month = i, delivery_time__year = year , delivery_Status = 'Return').count()
            data.append(jun)
        if i == 7:
            jul = Order.objects.filter(user_id = request.user.id,
                delivery_time__month = i, delivery_time__year = year , delivery_Status = 'Return').count()
            data.append(jul)
        if i == 8:
            aug = Order.objects.filter(user_id = request.user.id,
                delivery_time__month = i, delivery_time__year = year , delivery_Status = 'Return').count()
            data.append(aug)
        if i == 9:
            sep = Order.objects.filter(user_id = request.user.id,
                delivery_time__month = i, delivery_time__year = year , delivery_Status = 'Return').count()
            data.append(sep)
        if i == 10:
            octo = Order.objects.filter(user_id = request.user.id,
                delivery_time__month = i, delivery_time__year = year , delivery_Status = 'Return').count()
            data.append(octo)
        if i == 11:
            nov = Order.objects.filter(user_id = request.user.id,
                delivery_time__month = i, delivery_time__year = year , delivery_Status = 'Return').count()
            data.append(nov)
        if i == 12:
            dec = Order.objects.filter(user_id = request.user.id,
                delivery_time__month = i, delivery_time__year = year , delivery_Status = 'Return').count()
            data.append(dec)

    return JsonResponse(data={
        'labels': labels,
        'data': data,
    })


    
