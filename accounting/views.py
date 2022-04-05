from django.contrib.messages.api import error
from django.shortcuts import render, redirect, get_object_or_404, reverse
from user.models import User
from .models import *
from user.models import User, ReferralModel
from .forms import *
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib import messages
from .sslcommerz import *
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, Q
from datetime import timedelta, date
from courier.models import *
from rest_framework.generics import ListAPIView
from django.views.generic import CreateView, DetailView, UpdateView, ListView, DeleteView, TemplateView
from courier.serializers import CashCollectionSerializer
from django.contrib.auth.decorators import login_required
from .serializer import *
from user.models import Notification
import base64
# cost keywords=>>>>>> op= order placement, atw= add to wallet, wop= wallet order placement, gift= money transfer

# Create your views here.
today = date.today()
this_month = today - timedelta(days=30)


class MyWallet(LoginRequiredMixin, View):
    def get(self, request):
        user_id = request.user.id
        data = WalletModel.objects.filter(user=user_id)
        total = WalletModel.objects.filter(user=user_id).values(
            'amount').aggregate(Sum('amount'))
        cost_list = ["O.P.", "W.O.P.", "Gift"]
        cost = TransactionModel.objects.filter(reason__in=cost_list, user=user_id, tran_date__gte=this_month).values('amount').aggregate(
            Sum('amount'))
        refer_list = ['driver', 'delivery man', 'merchant', 'agent', 'user']
        reffer = ReferHistory.objects.filter(
            user=user_id, created_on__gte=this_month, type__in=refer_list).count()

        cash_b = TransactionModel.objects.filter(
            reason="cash back", user=user_id, tran_date__gte=this_month).values('amount').aggregate(Sum('amount'))

        cash_out = TransactionModel.objects.filter(
            reason="Cash Out", user=user_id, tran_date__gte=this_month).values('amount').aggregate(Sum('amount'))

        for k, v in cash_b.items():
            if v:
                cash_b = v
            else:
                cash_b = 0

        for k, v in cost.items():
            if v:
                cost = int(v) - int(cash_b)
            else:
                cost = 0

        for k, v in total.items():
            if v is not None:
                total = v
            else:
                total = 0
        for k, v in cash_out.items():
            if v:
                cash_out = v
            else:
                cash_out = 0
        context = {
            'data': data,
            'cost': cost,
            'reffer': reffer,
            'total': total,
            'id': user_id,
            'cash_out': cash_out,
        }
        return render(request, 'accounting/mywallet.html', context)


class PaymentView(LoginRequiredMixin, View):
    def get(self, request):
        user_id = request.user.id
        data = TransactionModel.objects.filter(user=user_id)
        context = {
            'data': data,
            'id': user_id
        }
        return render(request, 'accounting/payments.html', context)


@csrf_exempt
def payment_success(request, user_id, unique_id):
    if request.method == 'POST':
        unique_id = '#' + str(unique_id)
        data = request.POST
        try:
            order = get_object_or_404(Order, reference_id=unique_id)
            if order.paid:
                messages.success(
                    request, 'You had alrady paid for this order.')
            else:
                TransactionModel.objects.create(
                    user_id=user_id,
                    tran_id=data['tran_id'],
                    val_id=data['val_id'],
                    amount=data['amount'],
                    card_type=data['card_type'],
                    card_no=data['card_no'],
                    store_amount=data['store_amount'],
                    bank_tran_id=data['bank_tran_id'],
                    status=data['status'],
                    tran_date=data['tran_date'],
                    currency=data['currency'],
                    card_issuer=data['card_issuer'],
                    card_brand=data['card_brand'],
                    card_issuer_country=data['card_issuer_country'],
                    card_issuer_country_code=data['card_issuer_country_code'],
                    verify_sign=data['verify_sign'],
                    verify_sign_sha2=data['verify_sign_sha2'],
                    currency_rate=data['currency_rate'],
                    risk_title=data['risk_title'],
                    risk_level=data['risk_level'],
                    reason="A.T.W."
                )
                Order.objects.filter(reference_id=unique_id).update(
                    paid=True, tran_id=data['tran_id'], payment='Online')
                noti_msg = 'Payment of ' + unique_id + \
                    ' has been completed by ' + data['card_issuer'] + '.'
                order_data = get_object_or_404(Order, reference_id=unique_id)
                Notification.objects.create(
                    user_id=user_id, text=noti_msg, order_id=order_data.id, is_payment=True, is_activated=True)
                messages.success(request, 'Payment Successfully')
        except:
            messages.error(request, 'Something went wrong')
    return render(request, 'accounting/paysuccess.html', {'request.user.id': user_id})


@csrf_exempt
def payment_failed(request):
    messages.error(request, 'Failed to pay')
    return render(request, 'accounting/paysuccess.html')


@login_required(login_url='login')
def add_money(request):
    user_id = request.user.id
    if request.method == 'POST':
        amount = request.POST.get('amount')
        return redirect(sslcommerz_wallet_gateway(request, amount))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@csrf_exempt
def add_money_success(request, pk):
    if request.method == 'POST':
        data = request.POST
        try:
            TransactionModel.objects.create(
                user_id=pk,
                tran_id=data['tran_id'],
                val_id=data['val_id'],
                amount=data['amount'],
                card_type=data['card_type'],
                card_no=data['card_no'],
                store_amount=data['store_amount'],
                bank_tran_id=data['bank_tran_id'],
                status=data['status'],
                tran_date=data['tran_date'],
                currency=data['currency'],
                card_issuer=data['card_issuer'],
                card_brand=data['card_brand'],
                card_issuer_country=data['card_issuer_country'],
                card_issuer_country_code=data['card_issuer_country_code'],
                verify_sign=data['verify_sign'],
                verify_sign_sha2=data['verify_sign_sha2'],
                currency_rate=data['currency_rate'],
                risk_title=data['risk_title'],
                risk_level=data['risk_level'],
                reason="A.T.W."
            )
            WalletModel.objects.create(
                user_id=pk, amount=data['amount'], tr_method='Add money', tran_id=data['tran_id'])
            messages.success(request, 'Add to wallet Successfully')
        except:
            messages.warning(request, 'something went wrong')
    return render(request, 'accounting/paysuccess.html', {'id': pk})


@csrf_exempt
def add_money_failed(request):
    messages.warning(request, 'Failed to Add')
    return render(request, 'accounting/paysuccess.html')


@login_required(login_url='login')
def wallet_pay_success(request, r_id):
    user_id = request.user.id
    x = '#' + r_id
    data = WalletModel.objects.filter(user=user_id).values(
        'amount').aggregate(Sum('amount'))
    order_data = get_object_or_404(Order, reference_id=x)
    amount = int(order_data.amount)

    if not order_data.paid:
        tr_id = unique_trangection_id_generator()
        for k, v in data.items():
            if v is not None:
                credit = v
            else:
                credit = 0
        if amount <= credit:
            try:
                TransactionModel.objects.create(
                    user_id=user_id,
                    tran_id=tr_id,
                    val_id='N/A',
                    amount=amount,
                    card_type='wallet',
                    card_no='N/A',
                    store_amount=amount,
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
                    reason="W.O.P."
                )
                paid = amount * (-1)
                WalletModel.objects.create(
                    user_id=user_id, amount=paid, tr_method='Shipment', receiver_id=1, tran_id=tr_id)
                WalletModel.objects.create(
                    user_id=1, amount=amount, tr_method='Shipment', sender_id=user_id, tran_id=tr_id)
                noti_msg = 'Payment of ' + r_id + ' has been completed by wallet.'
                Notification.objects.create(
                    user_id=user_id, text=noti_msg, order_id=order_data.id, is_payment=True, is_activated=True)

                order_data.paid = True
                order_data.tran_id = tr_id
                order_data.payment = 'Wallet'
                order_data.save()
                messages.success(request, 'Payment Success')
            except:
                messages.warning(request, 'Something Went Wrong')
        else:
            order_data.payment = 'Cash'
            order_data.save()
            messages.warning(request, "You haven't enough money at wallet. ")
    else:
        messages.info(request, 'You had already paid for this order')
        return render(request, 'accounting/paysuccess.html', {'id': user_id})
    return render(request, 'accounting/paysuccess.html', {'id': user_id})


class PackageView(LoginRequiredMixin, View):

    def get(self, request):
        user_id = request.user.id
        data = Package.objects.all().order_by('-id')
        form = PackageForm()

        context = {
            'data': data,
            'form': form,
            'id': user_id,
            'total': len(data)
        }
        return render(request, 'accounting/package_create.html', context)

    def post(self, request):
        if request.user.is_superuser:
            form = PackageForm(request.POST)
            if form.is_valid():
                form.save()
            else:
                messages.error(request, 'Fill the form correctly')

            return redirect('PackageView')


def activate(request, id):
    url = request.META.get('HTTP_REFERER')
    data = get_object_or_404(Package, pk=id)
    if data.activate:
        data.activate = False
    else:
        data.activate = True
    data.save()
    return HttpResponseRedirect(url)


@login_required(login_url='login')
def edit_package(request, pk):
    if request.user.is_authenticated:
        user_id = request.user.id
        data = get_object_or_404(Package, pk=pk)
        form = PackageForm(instance=data)
        if request.method == 'POST':
            form = PackageForm(request.POST, instance=data)
            if form.is_valid():
                form.save()
                return redirect('PackageView')
        context = {
            'id': user_id,
            'form': form,
            'pk': pk,
        }
        return render(request, 'accounting/edit-package.html', context)


@login_required(login_url='login')
def delete_package(request, pk):
    if request.user.is_superuser:
        data = get_object_or_404(Package, pk=pk)
        data.delete()
        return redirect('PackageView')


class ReferPriceView(LoginRequiredMixin, View):

    def get(self, request):
        user_id = request.user.id
        data = ReferPrice.objects.all().order_by('-id')
        form = ReferPriceForm()
        context = {
            'data': data,
            'form': form,
            'id': user_id,
            'total': len(data)
        }
        return render(request, 'accounting/refer_price.html', context)

    def post(self, request):
        if request.user.is_superuser:
            refer_type = request.POST.get('refer_type')
            am = request.POST.get('price')
            try:
                data = get_object_or_404(ReferPrice, refer_type=refer_type)
                data.price = am
                data.save()
            except:
                ReferPrice.objects.create(refer_type=refer_type, price=am)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required(login_url='login')
def edit_refer_price(request, pk):
    if request.user.is_superuser:
        user_id = request.user.id
        data = get_object_or_404(ReferPrice, pk=pk)
        form = ReferPriceForm(instance=data)
        if request.method == 'POST':
            form = ReferPriceForm(request.POST, instance=data)
            if form.is_valid():
                form.save()
                return redirect('ReferPriceView')
        context = {
            'id': user_id,
            'form': form,
            'pk': pk,
        }
        return render(request, 'accounting/edit_refer.html', context)


@login_required(login_url='login')
def delete_refer_price(request, pk):
    if request.user.is_superuser:
        data = get_object_or_404(ReferPrice, pk=pk)
        data.delete()
        return redirect('ReferPriceView')


class AllTransactions(LoginRequiredMixin, TemplateView):
    template_name = 'accounting/all_trasection.html'


class AllTodayTransactions(LoginRequiredMixin, ListAPIView):
    serializer_class = TransactionModelSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            queryset = TransactionModel.objects.all()
            queryset = queryset.filter(tran_date__date=today)
            return queryset
        else:
            user_id = self.request.user.id
            queryset = TransactionModel.objects.all()
            queryset = queryset.filter(tran_date__date=today, user_id=user_id)


class AllThisMonthTransactions(LoginRequiredMixin, ListAPIView):
    serializer_class = TransactionModelSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            queryset = TransactionModel.objects.all()
            queryset = queryset.filter(tran_date__date__gte=this_month)
            return queryset
        else:
            user_id = self.request.user.id
            queryset = TransactionModel.objects.all()
            queryset = queryset.filter(
                tran_date__date__gte=this_month, user_id=user_id)
            return queryset


class AllTransactionsDateFilter(LoginRequiredMixin, ListAPIView):
    serializer_class = TransactionModelSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            queryset = TransactionModel.objects.all()
            queryset = queryset.filter(tran_date__date__gte=this_month)
            st = self.request.query_params.get('start')
            en = self.request.query_params.get('end')
            if st and en is not None:
                queryset = queryset.filter(
                    tran_date__date__gte=st, tran_date__date__lte=en)
            return queryset
        else:
            user_id = self.request.user.id
            queryset = TransactionModel.objects.all()
            queryset = queryset.filter(tran_date__date__gte=this_month)
            st = self.request.query_params.get('start')
            en = self.request.query_params.get('end')
            if st and en is not None:
                queryset = queryset.filter(
                    tran_date__date__gte=st, tran_date__date__lte=en, user_id=user_id)
            return queryset


class ReferHistoryView(LoginRequiredMixin, View):

    def get(self, request):
        data = ''
        user_id = request.user.id
        if request.user.is_superuser:
            data = ReferHistory.objects.all().order_by('-id')
        else:
            data = ReferHistory.objects.filter(user=user_id).order_by('-id')
        context = {
            'data': data,
            'id': user_id,
            'total': len(data)
        }
        return render(request, 'accounting/refer_history.html', context)


@login_required(login_url='login')
def money_transfer(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            data = request.POST
            rc = data['receiver']
            am = data['amount']
            user_id = request.user.id
            my_amount = WalletModel.objects.filter(
                user=user_id).values('amount').aggregate(Sum('amount'))
            try:
                val = int(am) * (-1)
                if my_amount:
                    for k, v in my_amount.items():
                        if v:
                            if int(v) >= int(am):
                                tr_id = unique_trangection_id_generator()
                                WalletModel.objects.create(
                                    user_id=user_id, amount=val, tr_method="Gift", receiver_id=rc, tran_id=tr_id)

                                WalletModel.objects.create(
                                    user_id=rc, amount=am, tr_method="Gift", sender_id=user_id, tran_id=tr_id)

                                TransactionModel.objects.create(
                                    user_id=user_id,
                                    tran_id=tr_id,
                                    val_id='N/A',
                                    amount=am,
                                    card_type='wallet',
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
                                    reason="Gift"
                                )
                                noti_msg = request.user.username + " has sent you " + am + 'tk. Gift.'
                                Notification.objects.create(
                                    user_id=rc, text=noti_msg, is_transfer=True, is_activated=True)

                                messages.success(
                                    request, 'Transferred Successfully')
                            else:
                                messages.warning(request, "Not Enough Credit")
                        else:
                            messages.warning(request, "Not Enough Credit")
            except:
                messages.warning(request, 'Something went Wrong')
        return HttpResponseRedirect(request.META['HTTP_REFERER'])


class CreateFAQ(LoginRequiredMixin, CreateView):
    form_class = FAQForm
    template_name = 'accounting/create_faq.html'


class HelpFAQS(LoginRequiredMixin, ListView):
    model = FAQModel
    template_name = 'accounting/faq_list.html'

    def get_queryset(self):
        queryset = FAQModel.objects.filter(faq_type='App')
        return queryset


class PrivacyFAQS(LoginRequiredMixin, ListView, ):
    model = FAQModel
    template_name = 'accounting/faq_list.html'

    def get_queryset(self):
        queryset = FAQModel.objects.filter(faq_type='Booking')
        return queryset


class UserHelpFAQS(ListView):
    model = FAQModel
    template_name = 'accounting/user_faq_list.html'

    def get_queryset(self):
        queryset = FAQModel.objects.filter(faq_type='App')
        return queryset


class UserPrivacyFAQS(ListView):
    model = FAQModel
    template_name = 'accounting/user_faq_list.html'

    def get_queryset(self):
        queryset = FAQModel.objects.filter(faq_type='Booking')
        return queryset


class FAQDetails(LoginRequiredMixin, DetailView):
    model = FAQModel
    template_name = 'accounting/faqdetails.html'


class FAQUpdate(LoginRequiredMixin, UpdateView):
    model = FAQModel
    form_class = FAQForm
    template_name = 'accounting/create_faq.html'


class FAQDelete(LoginRequiredMixin, DeleteView):
    model = FAQModel
    success_url = "/"
    template_name = 'courier/delete_order.html'


class FinishedView(LoginRequiredMixin, View):
    def get(self, request):
        user_id = request.user.id
        data = Order.objects.filter(driver=user_id, delivery_Status='Complete')
        num = Order.objects.filter(
            driver=user_id, delivery_Status='Complete').count()
        head = 'Finished'
        context = {
            'data': data,
            'num': num,
            'head': head
        }
        return render(request, 'courier/mydelivaries.html', context)


class AcceptedView(LoginRequiredMixin, View):
    def get(self, request):
        user_id = request.user.id
        head = 'Accepted'
        data = Order.objects.filter(
            Q(delivery_Status='Return') | Q(
                delivery_Status='Delivering') | Q(delivery_Status='Pending'),
            driver=user_id)
        num = len(data)
        context = {
            'data': data,
            'num': num,
            'head': head
        }
        return render(request, 'courier/mydelivaries.html', context)


@login_required(login_url='login')
def in_cash_collection(request):
    id_list = User.objects.filter(
        Q(is_driver=True) | Q(is_delivery_man=True)).distinct()
    if request.method == 'POST':
        collector = request.POST.get('collector')
        return redirect('in_cash_collection_report', collector)
    return render(request, 'accounting/cash_collector.html', {'data': id_list})


@login_required(login_url='login')
def in_cash_collection_report(request, collector):
    data = CashCollection.objects.filter(driver=collector)
    dr = ''
    for i in data:
        dr = i.driver.id

    context = {
        'dr': dr
    }
    return render(request, 'accounting/cash_colection report.html', context)


@login_required(login_url='login')
def in_collection_delete(request, pk):
    data = get_object_or_404(CashCollection, pk=pk)
    data.delete()
    return redirect('cash_collection')


@login_required(login_url='login')
def in_all_collection_delete(request, pk):
    data = CashCollection.objects.filter(driver=pk)
    for i in data:
        i.delete()
    return redirect('cash_collection')


@login_required(login_url='login')
def all_cash_collection(request):
    return render(request, 'accounting/all_cash_collection report.html')


@login_required(login_url='login')
def pay_now(request, pk):
    data = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        unique_id = data.reference_id
        unique_id = unique_id.replace('#', '')
        amount = data.amount
        pay_method = request.POST.get('method_type')

        if pay_method == 'Wallet':
            return redirect('wallet_pay_success', unique_id)
        elif pay_method == 'Online':
            return redirect(sslcommerz_payment_gateway(request, amount, unique_id))
        else:
            data.pay_method = 'Cash'
            data.save()
            return redirect('order_list')
    return render(request, 'accounting/pay_now.html')


@login_required(login_url='login')
def cash_back(user_id, am):
    try:
        tr_id = unique_trangection_id_generator()
        WalletModel.objects.create(
            user_id=user_id, amount=am, tr_method="cash back", tran_id=tr_id)

        TransactionModel.objects.create(
            user_id=user_id,
            tran_id=tr_id,
            val_id='N/A',
            amount=am,
            card_type='wallet',
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
            reason="cash back"
        )
    except:
        HttpResponse('Something went Wrong')


class SetPrices(LoginRequiredMixin, CreateView):
    form_class = PricesForm
    template_name = 'accounting/set_prices.html'
    success_url = '/price/'


class PriceList(LoginRequiredMixin, ListView):
    model = Prices
    template_name = 'accounting/prices.html'

    def get_queryset(self):
        price = Prices.objects.all().order_by("-id")[:1]
        return price


@login_required(login_url='login')
def money_withdraw(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            # ac = request.POST['acc_no']
            ac = 'FRT5OPFXKC'
            amount = request.POST['amount']
            remark = 'Cash Withdraw'
            response = refund_api(ac, amount, remark)
        return render(request, 'Accounting/refund.html')


def wallet_withdraw(request):
    if request.user.is_driver or request.user.is_delivery_man:
        user_id = request.user.id
        data = WalletModel.objects.filter(user=user_id).values(
            'amount').aggregate(Sum('amount'))

        if request.method == 'POST':
            tr_id = unique_trangection_id_generator()
            for k, v in data.items():
                if v is not None:
                    credit = v
                else:
                    credit = 0
            amount = request.POST.get('amount')
            if int(amount) <= credit:
                try:
                    TransactionModel.objects.create(
                        user_id=user_id,
                        tran_id=tr_id,
                        val_id='N/A',
                        amount=amount,
                        card_type='wallet',
                        card_no='N/A',
                        store_amount=amount,
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
                        reason="Cash Out"
                    )
                    paid = int(amount) * (-1)
                    WalletModel.objects.create(
                        user_id=user_id, amount=paid, tr_method='Cash Out', receiver_id=1, tran_id=tr_id)
                    WalletModel.objects.create(
                        user_id=1, amount=amount, tr_method='Cash Out', sender_id=user_id, tran_id=tr_id)
                    messages.success(request, 'Cash Out Successful')
                except:
                    messages.warning(request, 'Something Went Wrong')
            else:
                messages.warning(
                    request, "You haven't enough money at wallet. ")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


#        API
class InTodayCollection(LoginRequiredMixin, ListAPIView):
    serializer_class = CashCollectionSerializer

    def get_queryset(self):
        dr = self.request.query_params.get('dr')
        queryset = CashCollection.objects.all()
        queryset = queryset.filter(created_on=today, driver=dr)
        return queryset


class InThisMonthCollection(LoginRequiredMixin, ListAPIView):
    serializer_class = CashCollectionSerializer

    def get_queryset(self):
        dr = self.request.query_params.get('dr')
        queryset = CashCollection.objects.all()
        queryset = queryset.filter(created_on__gte=this_month, driver=dr)
        return queryset


class InCashCollectionDateFilter(LoginRequiredMixin, ListAPIView):
    serializer_class = CashCollectionSerializer

    def get_queryset(self):
        queryset = CashCollection.objects.all()
        st = self.request.query_params.get('start')
        en = self.request.query_params.get('end')
        dr = self.request.query_params.get('dr')
        if st and en is not None:
            queryset = queryset.filter(
                created_on__gte=st, created_on__lte=en, driver=dr)
        return queryset


class AllTodayCollection(LoginRequiredMixin, ListAPIView):
    serializer_class = CashCollectionSerializer

    def get_queryset(self):
        queryset = CashCollection.objects.all()
        queryset = queryset.filter(created_on=today)
        return queryset


class AllThisMonthCollection(LoginRequiredMixin, ListAPIView):
    serializer_class = CashCollectionSerializer

    def get_queryset(self):
        dr = self.request.query_params.get('dr')
        queryset = CashCollection.objects.all()
        queryset = queryset.filter(created_on__gte=this_month)
        return queryset


class AllCashCollectionDateFilter(LoginRequiredMixin, ListAPIView):
    serializer_class = CashCollectionSerializer

    def get_queryset(self):
        queryset = CashCollection.objects.all()
        st = self.request.query_params.get('start')
        en = self.request.query_params.get('end')
        if st and en is not None:
            queryset = queryset.filter(created_on__gte=st, created_on__lte=en)
        return queryset


from django.views.decorators.http import require_GET, require_POST
from webpush import send_user_notification
import json

def home(request):
   webpush_settings = getattr(settings, 'WEBPUSH_SETTINGS', {})
   vapid_key = webpush_settings.get('VAPID_PUBLIC_KEY')
   user = request.user
   return render(request, 'courier/test.html', {user: user, 'vapid_key': vapid_key})




@csrf_exempt
def send_push(request):
    try:
        body = request.body
        data = json.loads(body)

        if 'head' not in data or 'body' not in data or 'id' not in data:
            return JsonResponse(status=400, data={"message": "Invalid data format"})

        user_id = data['id']
        user = get_object_or_404(User, pk=user_id)
        payload = {'head': data['head'], 'body': data['body']}
        send_user_notification(user=user, payload=payload, ttl=1000)

        return JsonResponse(status=200, data={"message": "Web push successful"})
    except TypeError:
        return JsonResponse(status=500, data={"message": "An error occurred"})