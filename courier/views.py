import courier
from rest_framework.generics import ListAPIView
from accounting.models import Package
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.base import TemplateView
from django.views import View
from django.db.models import Sum
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
import datetime
from user import views
from json import dumps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from rest_framework import generics
import random
import math
from .serializers import NotificationSerializer, SelectPackageSerializer
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string

from .serializers import *
from .models import *
from .forms import *

from user.serializers import Notifications
from user.views import profile_visits
from user.models import *

from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from accounting.sslcommerz import *
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.core.mail import send_mail
import random

from accounting.views import cash_back
from accounting.models import *

from django.db.models import Sum, Q, Value, F
import datetime
from datetime import timedelta


today = datetime.datetime.today()
this_month = today - timedelta(days=30)


def user(user):
    return user.is_user is True


def driver(user):
    return user.is_driver is True


def delivery_man(user):
    return user.is_delivery_man is True


def agent(user):
    return user.is_agent is True


def merchant(user):
    return user.is_merchant is True


def admin(user):
    return user.is_superuser is True


class Admin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser is True


class Driver(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_driver is True


class DeliveryMan(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_delivery_man is True


@login_required
def dashboard(request):
    if request.user.is_superuser:
        id = request.user.id
        cash_col = {}
        date = datetime.datetime.now().month
        year = datetime.datetime.now().year
        monthly_delivery = Order.objects.filter(Q(delivery_Status='Complete') | Q(
            delivery_Status='Delivering'), delivery_time__month=date, delivery_time__year=year).count()
        client_list = User.objects.filter(is_user=True, is_active=True)
        merchant_list = User.objects.filter(is_merchant=True, is_active=True)
        mer_length = len(merchant_list)
        order_list = Order.objects.all()
        driver_list = User.objects.filter(
            is_driver=True, is_active=True).count()
        deliveryman_list = User.objects.filter(
            Q(is_delivery_man=True) | Q(is_driver=True), is_active=True)
        for c in deliveryman_list:
            am = CashCollection.objects.filter(driver=c.id, created_on=today).values(
                'amount').aggregate(Sum('amount'))
            for k, v in am.items():
                if v:
                    cash_col[c] = v

        agents_cash_total = 0
        total_complete_deliveries_agent = Order.objects.filter(
            user__is_agent=True, delivery_Status="Complete", delivery_time__month=date,
            delivery_time__year=year).count()

        total_cash_agent = Order.objects.filter(
            user__is_agent=True, delivery_Status="Complete", delivery_time__month=date,
            delivery_time__year=year).values('amount').aggregate(Sum('amount'))
        for k, v in total_cash_agent.items():
            if v:
                agents_cash_total = v
        income = 0
        cost = 0
        cost_data = WalletModel.objects.filter(created_on__gte=this_month).values(
            'amount').aggregate(Sum('amount'))
        shipment = Order.objects.filter(delivery_time__gte=this_month, paid=True).values(
            'amount').aggregate(Sum('amount'))
        order_cost = Order.objects.filter(delivery_time__gte=this_month, paid=True).values(
            'driver_amount').aggregate(Sum('driver_amount'))
        if shipment is not None:
            for k, v in shipment.items():
                if v is not None:
                    income += int(v)
                else:
                    income += 0
        method = ReferPrice.objects.all()
        for i in method:
            rt = i.refer_type
            refer_cost = ReferHistory.objects.filter(created_on__gte=this_month, type=rt).values('amount').aggregate(
                Sum('amount'))
            if refer_cost is not None:
                for k, v in refer_cost.items():
                    if v is not None:
                        cost += int(v)
                    else:
                        cost += 0
        oc = 0
        for k, v in order_cost.items():
            if v:
                oc += int(v)
            else:
                oc = 0
        cost += oc
        income = dumps(income)
        cost = dumps(cost)

        context = {
            'income': income,
            'cost': cost,
            'client_list': client_list,
            'merchant_list': merchant_list,
            'deliveryman_list': deliveryman_list,
            'order_list': order_list,
            'mer_length': mer_length,
            'driver_list': driver_list,
            'monthly_delivery': monthly_delivery,
            'cash_col': cash_col,
            'agents_cash_total': agents_cash_total,
            'total_complete_deliveries_agent': total_complete_deliveries_agent,
            'id': id,
        }
        return render(request, 'dashboards/admin.html', context)

    if request.user.is_driver:
        id = request.user.id
        return redirect('driver_dashboard')

    if request.user.is_merchant:
        id = request.user.id
        return redirect('merchant_dashboard')

    if request.user.is_agent:
        id = request.user.id
        return redirect('agent_dashboard')

    if request.user.is_delivery_man:
        id = request.user.id
        return redirect('deliveryman_dashboard')

    if request.user.is_user:
        id = request.user.id
        return redirect('user_dashboard')

    else:
        return redirect('login')


def merchant_dashboard(request):
    return render(request, 'dashboards/merchant.html')


@user_passes_test(agent)
def agent_dashboard(request):
    return render(request, 'dashboards/agent.html')


@user_passes_test(delivery_man, login_url='/accounts/login/')
def deliveryman_dashboard(request):
    time = datetime.datetime.now()
    month = time.strftime("%m")
    week = time.strftime("%U")
    day = time.strftime("%d")
    texts = Message.objects.filter(receiver=request.user)

    ratings = Ratings.objects.get(rated_user=request.user)
    rating = (ratings.avg_rating/5) * 100

    order_day = Order.objects.filter(
        driver=request.user, delivery_time__day=day)
    order_week = Order.objects.filter(
        driver=request.user, delivery_time__week=week)
    order_month = Order.objects.filter(
        driver=request.user, delivery_time__month=month)

    order_day_count = Order.objects.filter(
        driver=request.user, delivery_time__day=day).count()
    order_week_count = Order.objects.filter(
        driver=request.user, delivery_time__week=week).count()
    order_month_count = Order.objects.filter(
        driver=request.user, delivery_time__month=month).count()

    commision_day = Order.objects.filter(
        driver=request.user, delivery_time__day=day).aggregate(Sum('driver_amount'))
    commision_week = Order.objects.filter(
        driver=request.user, delivery_time__week=week).aggregate(Sum('driver_amount'))
    commision_month = Order.objects.filter(
        driver=request.user, delivery_time__month=month).aggregate(Sum('driver_amount'))

    amount_day = Order.objects.filter(
        driver=request.user, delivery_time__day=day).aggregate(Sum('amount'))
    amount_week = Order.objects.filter(
        driver=request.user, delivery_time__week=week).aggregate(Sum('amount'))
    amount_month = Order.objects.filter(
        driver=request.user, delivery_time__month=month).aggregate(Sum('amount'))

    total_deliveries = Order.objects.filter(
        driver=request.user, delivery_Status='Complete', delivery_time__month=month).count()

    total_pending_deliveries = Order.objects.filter(
        driver=request.user, delivery_Status='Pending', delivery_time__month=month).count()

    pending_orders = Order.objects.filter(
        driver=request.user, delivery_Status='Pending')

    january = Order.objects.filter(
        driver=request.user, delivery_Status='Complete', delivery_time__month=1).count()
    february = Order.objects.filter(
        driver=request.user, delivery_Status='Complete', delivery_time__month=2).count()
    march = Order.objects.filter(
        driver=request.user, delivery_Status='Complete', delivery_time__month=3).count()
    april = Order.objects.filter(
        driver=request.user, delivery_Status='Complete', delivery_time__month=4).count()
    may = Order.objects.filter(
        driver=request.user, delivery_Status='Complete', delivery_time__month=5).count()
    june = Order.objects.filter(
        driver=request.user, delivery_Status='Complete', delivery_time__month=6).count()
    july = Order.objects.filter(
        driver=request.user, delivery_Status='Complete', delivery_time__month=7).count()
    august = Order.objects.filter(
        driver=request.user, delivery_Status='Complete', delivery_time__month=8).count()
    september = Order.objects.filter(
        driver=request.user, delivery_Status='Complete', delivery_time__month=9).count()
    october = Order.objects.filter(
        driver=request.user, delivery_Status='Complete', delivery_time__month=10).count()
    november = Order.objects.filter(
        driver=request.user, delivery_Status='Complete', delivery_time__month=11).count()
    december = Order.objects.filter(
        driver=request.user, delivery_Status='Complete', delivery_time__month=12).count()
    january = dumps(january)
    february = dumps(february)
    march = dumps(march)
    april = dumps(april)
    may = dumps(may)
    june = dumps(june)
    july = dumps(july)
    august = dumps(august)
    september = dumps(september)
    october = dumps(october)
    november = dumps(november)
    december = dumps(december)
    context = {
        'january': january,
        'february': february,
        'march': march,
        'april': april,
        'may': may,
        'june': june,
        'july': july,
        'august': august,
        'september': september,
        'october': october,
        'november': november,
        'december': december,
        'pending_orders': pending_orders,
        'total_deliveries': total_deliveries,
        'total_pending_deliveries': total_pending_deliveries,
        'rating': rating,
        'order_month': order_month,
        'order_week': order_week,
        'order_day_count': order_day_count,
        'order_week_count': order_week_count,
        'order_month_count': order_month_count,
        'commision_day': commision_day['driver_amount__sum'],
        'commision_week': commision_week['driver_amount__sum'],
        'commision_month': commision_month['driver_amount__sum'],
        'amount_day': amount_day['amount__sum'],
        'amount_month': amount_month['amount__sum'],
        'amount_week': amount_week['amount__sum'],
        'texts': texts,
        'ratings': ratings
    }
    return render(request, 'dashboards/delivery_man.html', context)


@user_passes_test(driver, login_url='/accounts/login/')
def driver_dashboard(request):
    if request.user.is_driver:
        data = Order.objects.filter(
            driver=request.user, delivery_Status='Complete', delivery_time__month=today.month)
        this_month = Order.objects.filter(
            driver=request.user, delivery_Status='Complete', delivery_time__month=today.month).count()
        com = Order.objects.filter(
            driver=request.user, delivery_Status='Complete').count()
        deliv = Order.objects.filter(
            driver=request.user, delivery_Status='Delivering').count()
        context = {
            'com': com,
            'deliv': deliv,
            'data': data,
            'this_month': this_month,
        }
        return render(request, 'dashboards/driver_dashboard.html', context)


class DriverIncomeChart(LoginRequiredMixin, APIView):
    def get(self, request):
        january = Order.objects.filter(
            driver=request.user, delivery_Status='Complete', delivery_time__month=1).values(
            'driver_amount').aggregate(Sum('driver_amount'))
        february = Order.objects.filter(
            driver=request.user, delivery_Status='Complete', delivery_time__month=2).values(
            'driver_amount').aggregate(Sum('driver_amount'))
        march = Order.objects.filter(
            driver=request.user, delivery_Status='Complete', delivery_time__month=3).values(
            'driver_amount').aggregate(Sum('driver_amount'))
        april = Order.objects.filter(
            driver=request.user, delivery_Status='Complete', delivery_time__month=4).values(
            'driver_amount').aggregate(Sum('driver_amount'))
        may = Order.objects.filter(
            driver=request.user, delivery_Status='Complete', delivery_time__month=5).values(
            'driver_amount').aggregate(Sum('driver_amount'))
        june = Order.objects.filter(
            driver=request.user, delivery_Status='Complete', delivery_time__month=6).values(
            'driver_amount').aggregate(Sum('driver_amount'))
        july = Order.objects.filter(
            driver=request.user, delivery_Status='Complete', delivery_time__month=7).values(
            'driver_amount').aggregate(Sum('driver_amount'))
        august = Order.objects.filter(
            driver=request.user, delivery_Status='Complete', delivery_time__month=8).values(
            'driver_amount').aggregate(Sum('driver_amount'))
        september = Order.objects.filter(
            driver=request.user, delivery_Status='Complete', delivery_time__month=9).values(
            'driver_amount').aggregate(Sum('driver_amount'))
        october = Order.objects.filter(
            driver=request.user, delivery_Status='Complete', delivery_time__month=10).values(
            'driver_amount').aggregate(Sum('driver_amount'))
        november = Order.objects.filter(
            driver=request.user, delivery_Status='Complete', delivery_time__month=11).values(
            'driver_amount').aggregate(Sum('driver_amount'))
        december = Order.objects.filter(
            driver=request.user, delivery_Status='Complete', delivery_time__month=12).values(
            'driver_amount').aggregate(Sum('driver_amount'))
        data_list = [january, february, march, april, may, june,
                     july, august, september, october, november, december]
        for i in range(0, len(data_list)):
            for k, v in data_list[i].items():
                if v is not None:
                    data_list[i] = v
                else:
                    data_list[i] = 0

        data = {
            'january': data_list[0],
            'february': data_list[1],
            'march': data_list[2],
            'april': data_list[3],
            'may': data_list[4],
            'june': data_list[5],
            'july': data_list[6],
            'august': data_list[7],
            'september': data_list[8],
            'october': data_list[9],
            'november': data_list[10],
            'december': data_list[11]
        }
        return Response(data)


class NotificationLengthApi(LoginRequiredMixin, APIView):

    def get(self, request, format=None):
        notifications_length = ''
        user_id = request.user.id
        if request.user.is_delivery_man or request.user.is_driver:
            notifications_length = Order.objects.filter(accept=False).count()
            dr_noti = Notification.objects.filter(
                Q(is_manged=True) | Q(is_transfer=True), user=user_id,  is_seen=False).count()
            notifications_length += dr_noti

        elif request.user.is_user:
            notifications_length = Notification.objects.filter(Q(accept_user=True) | Q(pickup_finish=True) | Q(change_address=True) |
                                                               Q(finish=True)| Q(is_transfer=True), user=request.user, is_seen=False).count()
            print(notifications_length)

        elif request.user.is_superuser:
            notifications_length = Notification.objects.filter(
                Q(change_address=True)| Q(is_activated=False) | Q(is_payment=True), is_seen=False).count()
            transfer_noti = Notification.objects.filter(
                is_transfer=True, is_seen=False, user_id=user_id).count()
            notifications_length += transfer_noti
            
        context = [{
            'length': notifications_length,
            'driver': request.user.is_driver,
            'delivery man': request.user.is_delivery_man,
            'user': request.user.is_user,
            'admin': request.user.is_superuser,
        }]
        return Response(context)


class NotificationApi(LoginRequiredMixin, generics.ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Order.objects.all().order_by('-id')


class IndividualNotification(LoginRequiredMixin, generics.ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Order.objects.filter(driver=self.request.user)


class UserNotification(LoginRequiredMixin, generics.ListAPIView):
    serializer_class = Notifications

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-id')


class PackagePriceAPI(LoginRequiredMixin, ListAPIView):
    serializer_class = SelectPackageSerializer

    def get_queryset(self):
        queryset = Package.objects.all()
        kw = self.request.query_params.get('pk')
        if kw is not None:
            queryset = queryset.filter(pk=kw)
        return queryset


def create_order(request):
    id = request.user.id
    form = OrderForm()
    if request.method == 'POST':
        user_id = request.user.id
        form = OrderForm(request.POST)
        if form.is_valid():
            form_obj = form.save(commit=False)
            form_obj.user = request.user
            form_obj.delivery_Status = "Pending"
            pay_method = form.cleaned_data['payment']
            amount = form.cleaned_data['amount']
            date = datetime.datetime.now()
            form_obj.delivery_time = date
            timestamp = datetime.datetime.timestamp(date)
            unique_id = '#' + str(round(timestamp)) + \
                        "Ec" + str(request.user.id)
            form_obj.reference_id = unique_id
            if form_obj.delivery_latitude is None and form_obj.delivery_longitude is None:
                messages.success(request, 'Please Enter Delivery Location')
                return redirect('create_order')
            elif form_obj.pick_up_latitude is None and form_obj.pick_up_longitude is None:
                form_obj.save()
                return redirect('set_pickup_location', id)
            else:
                if pay_method == 'Wallet':
                    r_id = unique_id.replace('#', '')
                    form_obj.save()
                    return redirect('wallet_pay_success', r_id)
                elif pay_method == 'Online':
                    form_obj.save()
                    return redirect(sslcommerz_payment_gateway(request, amount, unique_id))
                else:
                    form_obj.pay_method = 'Cash'
                    form_obj.save()
                    return redirect('order_list')
    package = Package.objects.filter(activate=True)
    prices = Prices.objects.all().order_by('-id')
    context = {
        'form': form,
        'id': id,
        'package': package,
        'prices': prices
    }
    return render(request, 'courier/create_order.html', context)


def accept_user(request, id):
    url = request.META.get('HTTP_REFERER')
    user = Order.objects.get(pk=id)
    if user.accept is True:
        user.accept = False
    else:
        user.accept = True
    user.delivery_Status = 'Delivering'
    user.driver = request.user
    user.save()
    notification = Notification(
        user=user.user, driver=request.user, accept_user=True, is_activated=True, order_id=id)
    notification.save()
    return HttpResponseRedirect(url)


@login_required
def order_list(request):
    id = request.user.id
    if request.user.is_superuser:
        object_list = Order.objects.all()
    else:
        object_list = Order.objects.filter(user=request.user)
    context = {
        'object_list': object_list,
        'id': id
    }
    return render(request, 'courier/order_list.html', context)


class OrderDetails(LoginRequiredMixin, DetailView):
    model = Order
    pk = 'pk'
    template_name = "courier/order_details.html"

    def get_context_data(self, **kwargs):
        context = super(OrderDetails, self).get_context_data(**kwargs)
        context['id'] = self.request.user.id
        pk = self.kwargs.get(self.pk)
        return context


@login_required
def notification_order_details(request, pk):
    if request.user.is_superuser:
        data = get_object_or_404(Order, pk=pk)
        Notification.objects.filter(order_id=pk).update(is_seen=True)
        return render(request, 'courier/order_details.html', {'object': data})


class OrderUpdate(LoginRequiredMixin, UpdateView):
    model = Order
    fields = "__all__"
    success_url = "/order-list"
    template_name = "courier/edit_order.html"

    def get_context_data(self, **kwargs):
        context = super(OrderUpdate, self).get_context_data(**kwargs)
        context['id'] = self.request.user.id
        return context


def otp_sender(pk):
    digits = [i for i in range(0, 10)]
    random_str = ""
    data = get_object_or_404(Order, pk=pk)
    recipient_email = data.receiver_Email
    for i in range(6):
        index = math.floor(random.random() * 10)
        random_str += str(digits[index])
    data.otp = random_str
    data.save()
    body = "Hi, \n We noticed that you recently receive an order. \n Please confirm order by code bellow:\n" + \
        random_str + "\nThanks for choosing us. \nThis message was sent to you by E-courier"
    send_mail(subject='Verify Order', message=body,
              from_email='djangoapptest@essential-infotech.dev', recipient_list=[recipient_email], fail_silently=False)


class OrderStatusUpdate(LoginRequiredMixin, UpdateView):

    def get(self, request, pk):
        object = get_object_or_404(Order, pk=pk)
        arr = ['Return', 'Delivering', 'Pending', 'Complete']
        context = {
            'arr': arr,
            'id': request.user.id
        }
        return render(request, 'courier/status_edit_order.html', context)

    def post(self, request, pk):
        user = request.user.id
        object = get_object_or_404(Order, pk=pk)
        stat = object.payment
        dl_stat = request.POST.get('delivery_Status')

        if stat == 'Cash' and dl_stat == 'Complete':
            otp_sender(pk)
            return redirect('confirm_order_delivery', pk)
        else:
            obj = Order.objects.get(pk=pk)
            obj.delivery_Status = dl_stat
            obj.delivery_time = today
            obj.save()
            return redirect('AcceptedView')


def finish_otp(request, pk):
    otp_sender(pk)
    return redirect('confirm_order_delivery', pk)


def cancel_order(request, pk):
    user_id = request.user.id
    order = get_object_or_404(Order, pk=pk)
    data = ''
    if order.delivery_Status == 'Pending':
        order.delete()
        messages.info(request, 'Order Cancel Successful')

        if order.paid:
            cash_back(user_id, order.amount)
            order.delete()
            messages.info(
                request, "Order Cancel and cash back Successful. Check your wallet")
    else:
        messages.info(request, "Order Cancel Failed")

    return redirect('order_list')


def finish(request, pk):
    if request.method == 'POST':
        user = request.user.id
        otp = request.POST.get('otp')
        data = get_object_or_404(Order, pk=pk)
        am = data.amount
        try:
            if data.otp == otp:
                obj = Order.objects.get(pk=pk)
                obj.paid = True
                obj.delivery_Status = 'Complete'
                obj.delivery_time = today
                obj.otp = ''
                obj.save()
                notification = Notification(
                    user=obj.user, order_id=pk, finish=True, driver=request.user)
                notification.save()
                collection = CashCollection.objects.filter(order=pk)
                if not collection:
                    CashCollection.objects.create(order=Order(
                        id=pk), driver=User(id=user), amount=am)
                return redirect('order_list')
        except:
            return HttpResponse('Something Went Wrong')
    return render(request, 'courier/conf_delivery.html', {'pk': pk})


class DeleteOrder(Admin, DeleteView):
    model = Order
    success_url = "/order-list"
    template_name = "courier/delete_order.html"

    def get_context_data(self, **kwargs):
        context = super(DeleteOrder, self).get_context_data(**kwargs)
        context['id'] = self.request.user.id
        messages.success(self.request, 'Order Deleted')
        return context


def set_pickup_location(request, id):
    pickup = Order.objects.get(id=id)
    form = OrderForm(instance=pickup)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=pickup)
        if form.is_valid():
            data = form.save(commit=False)
            if data.payment == 'Wallet':
                r_id = data.reference_id.replace('#', '')
                data.save()
                return redirect('wallet_pay_success', r_id)
            elif data.payment == 'Online':
                data.save()
                return redirect(sslcommerz_payment_gateway(request, data.amount, data.reference_id))
            else:
                data.payment = 'Cash'
                data.save()
                return redirect('order_list')
    return render(request, 'courier/map/change_pickup_location.html', {'form': form})


def change_pickup_location(request, id):
    pickup = Order.objects.get(id=id)
    form = OrderForm(instance=pickup)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=pickup)
        if form.is_valid():
            form.save()
            return redirect('user_delivery_tracking', id)
    return render(request, 'courier/map/change_pickup_location.html', {'form': form})


def delivery_location_change_request(id):
    data = get_object_or_404(Order, id=id)
    recipient_email = data.receiver_Email
    link = render_to_string(
        'courier/delivery_address_change_mail.html', {'data': data})
    body = "There is an address change request " + link
    send_mail(subject='Address Change Request', message=body,
              from_email=recipient_email, recipient_list=['colaborationw@gmail.com'], fail_silently=False)


def change_delivery_location(request, id):
    Notification.objects.filter(order_id=id).update(is_seen=True)
    delivery = Order.objects.get(id=id)
    form = OrderForm(instance=delivery)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=delivery)
        if form.is_valid():
            confirm = form.save(commit=False)
            confirm.confirm_change_delivery_address = True
            delivery_location_change_request(id)
            messages.success(
                request, "We will connect to you shortly to confirm the request")
            form.save()
            return redirect('user_delivery_tracking', id)
    return render(request, 'courier/map/change_delivery_location.html', {'form': form, 'delivery': delivery})


def approve_delivery_address_change(request, id):
    url = request.META.get('HTTP_REFERER')
    user = Order.objects.get(pk=id)
    user.approve_change_delivery_address = True
    user.delivery_latitude = user.change_latitude
    user.delivery_longitude = user.change_longitude
    user.save()
    notification = Notification(
        user=user.user, order_id=id, change_address=True, driver=request.user)
    notification.save()
    return HttpResponseRedirect(url)


def track_page(request):
    orders = Order.objects.filter(
        user=request.user, delivery_Status='Delivering')
    return render(request, 'courier/map/track_page.html', {'orders': orders})


def user_delivery_tracking(request, id):
    location = Order.objects.get(id=id)
    pick_up = []
    delivery = []
    delivery_man = []
    contact = ''
    pickup_finish = ''
    order_id = id
    pickup_finish = location.pickup_finish

    delivery.append(float(location.delivery_latitude))
    delivery.append(float(location.delivery_longitude))

    pick_up.append(float(location.pick_up_latitude))
    pick_up.append(float(location.pick_up_longitude))

    if location.driver is None:
        pass
    else:
        delivery_man.append(float(location.driver.latitude))
        delivery_man.append(float(location.driver.longitude))
        contact = location.driver.contact

    pick_up = dumps(pick_up)
    delivery = dumps(delivery)
    delivery_man = dumps(delivery_man)
    contact = dumps(contact)
    pickup_finish = dumps(pickup_finish)

    context = {
        'order_id': order_id,
        'pick_up': pick_up,
        'delivery': delivery,
        'delivery_man': delivery_man,
        'contact': contact,
        'pickup_finish': pickup_finish
    }
    return render(request, 'courier/map/user_delivery_tracking.html', context)


def pick_up_locations(request):
    order1 = Order.objects.filter(
        accept=True, driver=request.user, pickup_finish=False).order_by("-id")[:1]
    order2 = Order.objects.filter(
        accept=True, driver=request.user, pickup_finish=False).order_by("-id")[1:2]
    order3 = Order.objects.filter(
        accept=True, driver=request.user, pickup_finish=False).order_by("-id")[2:3]
    order4 = Order.objects.filter(
        accept=True, driver=request.user, pickup_finish=False).order_by("-id")[3:4]
    order5 = Order.objects.filter(
        accept=True, driver=request.user, pickup_finish=False).order_by("-id")[4:5]
    order6 = Order.objects.filter(
        accept=True, driver=request.user, pickup_finish=False).order_by("-id")[5:6]
    order7 = Order.objects.filter(
        accept=True, driver=request.user, pickup_finish=False).order_by("-id")[6:7]
    order8 = Order.objects.filter(
        accept=True, driver=request.user, pickup_finish=False).order_by("-id")[7:8]
    order9 = Order.objects.filter(
        accept=True, driver=request.user, pickup_finish=False).order_by("-id")[8:9]
    order10 = Order.objects.filter(
        accept=True, driver=request.user, pickup_finish=False).order_by("-id")[9:10]

    id_1 = ''
    id_2 = ''
    id_3 = ''
    id_4 = ''
    id_5 = ''
    id_6 = ''
    id_7 = ''
    id_8 = ''
    id_9 = ''
    id_10 = ''

    pick_up1 = []
    pick_up2 = []
    pick_up3 = []
    pick_up4 = []
    pick_up5 = []
    pick_up6 = []
    pick_up7 = []
    pick_up8 = []
    pick_up9 = []
    pick_up10 = []

    start1 = ''
    start2 = ''
    start3 = ''
    start4 = ''
    start5 = ''
    start6 = ''
    start7 = ''
    start8 = ''
    start9 = ''
    start10 = ''

    for i in order1:
        id_1 = i.id
        start1 = i.start
        pick_up1.append(i.pick_up_latitude)
        pick_up1.append(i.pick_up_longitude)

    for i in order2:
        id_2 = i.id
        start2 = i.start
        pick_up2.append(i.pick_up_latitude)
        pick_up2.append(i.pick_up_longitude)

    for i in order3:
        id_3 = i.id
        start3 = i.start
        pick_up3.append(i.pick_up_latitude)
        pick_up3.append(i.pick_up_longitude)

    for i in order4:
        id_4 = i.id
        start4 = i.start
        pick_up4.append(i.pick_up_latitude)
        pick_up4.append(i.pick_up_longitude)

    for i in order5:
        id_5 = i.id
        start5 = i.start
        pick_up5.append(i.pick_up_latitude)
        pick_up5.append(i.pick_up_longitude)

    for i in order6:
        id_6 = i.id
        start6 = i.start
        pick_up6.append(i.pick_up_latitude)
        pick_up6.append(i.pick_up_longitude)

    for i in order7:
        id_7 = i.id
        start7 = i.start
        pick_up7.append(i.pick_up_latitude)
        pick_up7.append(i.pick_up_longitude)

    for i in order8:
        id_8 = i.id
        start8 = i.start
        pick_up8.append(i.pick_up_latitude)
        pick_up8.append(i.pick_up_longitude)

    for i in order9:
        id_9 = i.id
        start9 = i.start
        pick_up9.append(i.pick_up_latitude)
        pick_up9.append(i.pick_up_longitude)

    for i in order10:
        id_10 = i.id
        start10 = i.start
        pick_up10.append(i.pick_up_latitude)
        pick_up10.append(i.pick_up_longitude)

    pick_up1 = dumps(pick_up1)
    pick_up2 = dumps(pick_up2)
    pick_up3 = dumps(pick_up3)
    pick_up4 = dumps(pick_up4)
    pick_up5 = dumps(pick_up5)
    pick_up6 = dumps(pick_up6)
    pick_up7 = dumps(pick_up7)
    pick_up8 = dumps(pick_up8)
    pick_up9 = dumps(pick_up9)
    pick_up10 = dumps(pick_up10)

    id_1 = dumps(id_1)
    id_2 = dumps(id_2)
    id_3 = dumps(id_3)
    id_4 = dumps(id_4)
    id_5 = dumps(id_5)
    id_6 = dumps(id_6)
    id_7 = dumps(id_7)
    id_8 = dumps(id_8)
    id_9 = dumps(id_9)
    id_10 = dumps(id_10)

    start1 = dumps(start1)
    start2 = dumps(start2)
    start3 = dumps(start3)
    start4 = dumps(start4)
    start5 = dumps(start5)
    start6 = dumps(start6)
    start7 = dumps(start7)
    start8 = dumps(start8)
    start9 = dumps(start9)
    start10 = dumps(start10)

    context = {
        'pick_up1': pick_up1,
        'pick_up2': pick_up2,
        'pick_up3': pick_up3,
        'pick_up4': pick_up4,
        'pick_up5': pick_up5,
        'pick_up6': pick_up6,
        'pick_up7': pick_up7,
        'pick_up8': pick_up8,
        'pick_up9': pick_up9,
        'pick_up10': pick_up10,
        'id_1': id_1,
        'id_2': id_2,
        'id_3': id_3,
        'id_4': id_4,
        'id_5': id_5,
        'id_6': id_6,
        'id_7': id_7,
        'id_8': id_8,
        'id_9': id_9,
        'id_10': id_10,
        'start1': start1,
        'start2': start2,
        'start3': start3,
        'start4': start4,
        'start5': start5,
        'start6': start6,
        'start7': start7,
        'start8': start8,
        'start9': start9,
        'start10': start10,
    }
    return render(request, 'courier/map/pick_up_locations.html', context)


def start_pickup(request, id):
    order = Order.objects.get(id=id)
    form = OrderForm(instance=order)
    if request.method == "POST":
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            pickup_finish = form.save(commit=False)
            pickup_finish.pickup_finish = True
            form.save()
            notification = Notification(
                user=order.user, order_id=id, pickup_finish=True, driver=request.user)
            notification.save()
            return redirect('pick_up_locations')
    return render(request, 'courier/map/start_pickup.html', {'form': form, 'order': order})


def start_delivery(request):
    order1 = Order.objects.filter(
        driver=request.user, pickup_finish=True).order_by("-id")[:1]
    order2 = Order.objects.filter(
        driver=request.user, pickup_finish=True).order_by("-id")[1:2]
    order3 = Order.objects.filter(
        driver=request.user, pickup_finish=True).order_by("-id")[2:3]
    order4 = Order.objects.filter(
        driver=request.user, pickup_finish=True).order_by("-id")[3:4]
    order5 = Order.objects.filter(
        driver=request.user, pickup_finish=True).order_by("-id")[4:5]
    order6 = Order.objects.filter(
        driver=request.user, pickup_finish=True).order_by("-id")[5:6]
    order7 = Order.objects.filter(
        driver=request.user, pickup_finish=True).order_by("-id")[6:7]
    order8 = Order.objects.filter(
        driver=request.user, pickup_finish=True).order_by("-id")[7:8]
    order9 = Order.objects.filter(
        driver=request.user, pickup_finish=True).order_by("-id")[8:9]
    order10 = Order.objects.filter(
        driver=request.user, pickup_finish=True).order_by("-id")[9:10]

    id_1 = ''
    id_2 = ''
    id_3 = ''
    id_4 = ''
    id_5 = ''
    id_6 = ''
    id_7 = ''
    id_8 = ''
    id_9 = ''
    id_10 = ''

    delivery1 = []
    delivery2 = []
    delivery3 = []
    delivery4 = []
    delivery5 = []
    delivery6 = []
    delivery7 = []
    delivery8 = []
    delivery9 = []
    delivery10 = []

    contact1 = ''
    contact2 = ''
    contact3 = ''
    contact4 = ''
    contact5 = ''
    contact6 = ''
    contact7 = ''
    contact8 = ''
    contact9 = ''
    contact10 = ''

    for i in order1:
        id_1 = i.id
        contact1 = i.receiver_Contact
        delivery1.append(i.delivery_latitude)
        delivery1.append(i.delivery_longitude)

    for i in order2:
        id_2 = i.id
        contact2 = i.receiver_Contact
        delivery2.append(i.delivery_latitude)
        delivery2.append(i.delivery_longitude)

    for i in order3:
        id_3 = i.id
        contact3 = i.receiver_Contact
        delivery3.append(i.delivery_latitude)
        delivery3.append(i.delivery_longitude)

    for i in order4:
        id_4 = i.id
        contact4 = i.receiver_Contact
        delivery4.append(i.delivery_latitude)
        delivery4.append(i.delivery_longitude)

    for i in order5:
        id_5 = i.id
        contact5 = i.receiver_Contact
        delivery5.append(i.delivery_latitude)
        delivery5.append(i.delivery_longitude)

    for i in order6:
        id_6 = i.id
        contact6 = i.receiver_Contact
        delivery6.append(i.delivery_latitude)
        delivery6.append(i.delivery_longitude)

    for i in order7:
        id_7 = i.id
        contact7 = i.receiver_Contact
        delivery7.append(i.delivery_latitude)
        delivery7.append(i.delivery_longitude)

    for i in order8:
        id_8 = i.id
        contact8 = i.receiver_Contact
        delivery8.append(i.delivery_latitude)
        delivery8.append(i.delivery_longitude)

    for i in order9:
        id_9 = i.id
        contact9 = i.receiver_Contact
        delivery9.append(i.delivery_latitude)
        delivery9.append(i.delivery_longitude)

    for i in order10:
        id_10 = i.id
        contact10 = i.receiver_Contact
        delivery10.append(i.delivery_latitude)
        delivery10.append(i.delivery_longitude)

    delivery1 = dumps(delivery1)
    delivery2 = dumps(delivery2)
    delivery3 = dumps(delivery3)
    delivery4 = dumps(delivery4)
    delivery5 = dumps(delivery5)
    delivery6 = dumps(delivery6)
    delivery7 = dumps(delivery7)
    delivery8 = dumps(delivery8)
    delivery9 = dumps(delivery9)
    delivery10 = dumps(delivery10)

    id_1 = dumps(id_1)
    id_2 = dumps(id_2)
    id_3 = dumps(id_3)
    id_4 = dumps(id_4)
    id_5 = dumps(id_5)
    id_6 = dumps(id_6)
    id_7 = dumps(id_7)
    id_8 = dumps(id_8)
    id_9 = dumps(id_9)
    id_10 = dumps(id_10)

    contact1 = dumps(contact1)
    contact2 = dumps(contact2)
    contact3 = dumps(contact3)
    contact4 = dumps(contact4)
    contact5 = dumps(contact5)
    contact6 = dumps(contact6)
    contact7 = dumps(contact7)
    contact8 = dumps(contact8)
    contact9 = dumps(contact9)
    contact10 = dumps(contact10)

    context = {
        'delivery1': delivery1,
        'delivery2': delivery2,
        'delivery3': delivery3,
        'delivery4': delivery4,
        'delivery5': delivery5,
        'delivery6': delivery6,
        'delivery7': delivery7,
        'delivery8': delivery8,
        'delivery9': delivery9,
        'delivery10': delivery10,
        'id_1': id_1,
        'id_2': id_2,
        'id_3': id_3,
        'id_4': id_4,
        'id_5': id_5,
        'id_6': id_6,
        'id_7': id_7,
        'id_8': id_8,
        'id_9': id_9,
        'id_10': id_10,

        'contact1': contact1,
        'contact2': contact2,
        'contact3': contact3,
        'contact4': contact4,
        'contact5': contact5,
        'contact6': contact6,
        'contact7': contact7,
        'contact8': contact8,
        'contact9': contact9,
        'contact10': contact10,
    }
    return render(request, 'courier/map/start_delivery.html', context)


class CompletedReport(LoginRequiredMixin, View):
    def get(self, request):
        user_id = request.user.id
        if request.user.is_user:
            object_list = Order.objects.filter(user=user_id, delivery_Status='Complete')

        elif request.user.is_driver or request.user.is_delivery_man:
            object_list = Order.objects.filter(driver=user_id, delivery_Status='Complete')

        elif request.user.is_superuser:
            object_list = Order.objects.filter(delivery_Status='Complete')
        context = {
            'object_list': object_list,
            'id': user_id
        }
        return render(request, 'courier/complete_order.html', context)


class DeliveringReport(LoginRequiredMixin, View):
    def get(self, request):
        user_id = request.user.id
        if request.user.is_user:
            object_list = Order.objects.filter(user=user_id, delivery_Status='Delivering')

        elif request.user.is_driver or request.user.is_delivery_man:
            object_list = Order.objects.filter(driver=user_id, delivery_Status='Delivering')

        elif request.user.is_superuser:
            object_list = Order.objects.filter(delivery_Status='Delivering')
            
        context = {
            'object_list': object_list,
            'id': user_id
        }
        return render(request, 'courier/delivering_order.html', context)


class PendingReport(LoginRequiredMixin, View):
    def get(self, request):
        user_id = request.user.id
        if request.user.is_user:
            object_list = Order.objects.filter(user=user_id, delivery_Status='Pending')

        elif request.user.is_driver or request.user.is_delivery_man:
            object_list = Order.objects.filter(driver=user_id, delivery_Status='Pending')

        elif request.user.is_superuser:
            object_list = Order.objects.filter(delivery_Status='Pending')

        context = {
            'object_list': object_list,
            'id': user_id
        }
        return render(request, 'courier/pending_order.html', context)


class ReturnReport(LoginRequiredMixin, View):
    def get(self, request):
        user_id = request.user.id
        if request.user.is_user:
            object_list = Order.objects.filter(user=user_id, delivery_Status='Return')

        elif request.user.is_driver or request.user.is_delivery_man:
            object_list = Order.objects.filter(driver=user_id, delivery_Status='Return')

        elif request.user.is_superuser:
            object_list = Order.objects.filter(delivery_Status='Return')

        context = {
            'object_list': object_list,
            'id': user_id
        }
        return render(request, 'courier/return_order.html', context)


@login_required
def invoice_generator(request, pk):
    data = Order.objects.filter(pk=pk)
    ref = ''
    user_id = request.user.id
    for i in data:
        userid = i.user
        ref = i.reference_id
    user_data = User.objects.filter(pk=user_id)
    filename = ref + ".pdf"
    img = f'C:/Users/HP.LAPTOP-6KVK1FFU/Desktop/cl-courier/static/assets/media/logo.png'
    context = {'data': data, 'user': user_data, 'img': img}

    response = HttpResponse(content_type='application/pdf')

    response['Content-Disposition'] = "attachment; filename= %s" % filename

    template = get_template('courier/invoice.html')
    html = template.render(context)
    # , link_callback=link_callback)
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response
    return render(request, 'courier/invoice.html', context)


@csrf_exempt
@login_required
def change_location_data(request):
    if request.method == 'POST':
        if request.user.is_delivery_man or request.user.is_driver:
            user_id = request.user.id
            data = request.POST
            User.objects.filter(pk=user_id).update(
                latitude=data['lt'], longitude=data['ln'])
    return HttpResponse('ok')


class DeliverymanLocation(LoginRequiredMixin, APIView):
    def get(self, request):
        if request.user.is_delivery_man:
            id = request.user.id
            driver = User.objects.get(id=id)
            data = [{
                'latitude': driver.latitude,
                'longitude': driver.longitude
            }]
            return Response(data)


@csrf_exempt
@login_required
def manage_commission(request):
    if request.method == 'POST':
        com_type = request.POST['com_type']
        dr_com = request.POST['dr_com']
        obj_id = request.POST['obj_id']
        data = get_object_or_404(Order, pk=obj_id)
        dr_id = data.driver.id
        sender_id = request.user.id
        if data.driver:
            if com_type == 'Percentage':
                am = data.amount
                dr_am = (int(am) * int(dr_com))/100
                data.driver_amount = int(dr_am)
                data.save()
                try:
                    tr_id = unique_trangection_id_generator()
                    WalletModel.objects.create(user_id=dr_id, amount=dr_am, tr_method="Commission",
                                               tran_id=tr_id, sender_id=sender_id)
                    noti_msg = request.user.username + \
                        " Sent you commission for order no " + data.reference_id
                    Notification.objects.create(
                        user_id=dr_id, text=noti_msg, is_manged=True, is_activated=True)
                    TransactionModel.objects.create(
                        user_id=dr_id,
                        tran_id=tr_id,
                        val_id='N/A',
                        amount=am,
                        card_type='N/A',
                        card_no='N/A',
                        store_amount=am,
                        bank_tran_id='N/A',
                        status='Paid',
                        tran_date=datetime.datetime.today(),
                        currency='BDT',
                        card_issuer='N/A',
                        card_brand='N/A',
                        card_issuer_country='N/A',
                        card_issuer_country_code='N/A',
                        verify_sign='N/A',
                        verify_sign_sha2='N/A',
                        currency_rate=1.00,
                        risk_title='Safe',
                        risk_level=0,
                        reason="Commission"
                    )

                    messages.success(request, 'Commission Sent Successfully')
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                except:
                    messages.info(request, 'Something went Wrong')

            elif com_type == 'Amount':
                data.driver_amount = dr_com
                data.save()
                dr_id = data.driver.id
                try:
                    tr_id = unique_trangection_id_generator()
                    WalletModel.objects.create(
                        user_id=dr_id, amount=dr_com, tr_method="Commission", tran_id=tr_id, sender_id=sender_id)
                    noti_msg = request.user.username + \
                        " Sent you commission for order no " + data.reference_id
                    Notification.objects.create(
                        user_id=dr_id, text=noti_msg, is_manged=True)
                    TransactionModel.objects.create(
                        user_id=dr_id,
                        tran_id=tr_id,
                        val_id='N/A',
                        amount=dr_com,
                        card_type='N/A',
                        card_no='N/A',
                        store_amount=dr_com,
                        bank_tran_id='N/A',
                        status='Paid',
                        tran_date=datetime.datetime.today(),
                        currency='BDT',
                        card_issuer='N/A',
                        card_brand='N/A',
                        card_issuer_country='N/A',
                        card_issuer_country_code='N/A',
                        verify_sign='N/A',
                        verify_sign_sha2='N/A',
                        currency_rate=1.00,
                        risk_title='Safe',
                        risk_level=0,
                        reason="Commission"
                    )

                    messages.success(request, 'Commission Sent Successfully')
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                except:
                    messages.info(request, 'Something went Wrong')

        else:
            messages(request, 'No one accepted this order')
        return HttpResponse('ok')

    return redirect('MyWallet')


def manage_commission_seen(request, pk):
    data = get_object_or_404(Notification, pk=pk)
    data.is_seen = True
    data.save()
    return redirect('MyWallet')


@login_required
def user_track(request, id):
    Notification.objects.filter(order_id=id).update(is_seen=True)
    location = Order.objects.get(id=id)
    pick_up = []
    delivery = []
    delivery_man = []
    contact = ''
    pickup_finish = ''
    order_id = id
    pickup_finish = location.pickup_finish

    delivery.append(float(location.delivery_latitude))
    delivery.append(float(location.delivery_longitude))

    pick_up.append(float(location.pick_up_latitude))
    pick_up.append(float(location.pick_up_longitude))

    if location.driver is None:
        pass
    else:
        delivery_man.append(float(location.driver.latitude))
        delivery_man.append(float(location.driver.longitude))
        contact = location.driver.contact

    pick_up = dumps(pick_up)
    delivery = dumps(delivery)
    delivery_man = dumps(delivery_man)
    contact = dumps(contact)
    pickup_finish = dumps(pickup_finish)

    context = {
        'order_id': order_id,
        'pick_up': pick_up,
        'delivery': delivery,
        'delivery_man': delivery_man,
        'contact': contact,
        'pickup_finish': pickup_finish
    }
    return render(request, 'courier/map/user_delivery_tracking.html', context)


@login_required
def details(request, pk):
    data = get_object_or_404(Order, pk=pk)
    Notification.objects.filter(order_id=pk).update(is_seen=True)
    return render(request, 'courier/order_details.html', {'object': data})
