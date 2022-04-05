from os import name
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import *
urlpatterns = [
    path('my/wallet/', MyWallet.as_view(), name='MyWallet'),
    path('add/to/wallet/', add_money, name='add_money'),
    path('add/success/<int:pk>/', add_money_success, name='add_money_success'),
    path('failed/add/', add_money_failed, name='add_money_failed'),

    path('money/transfer/', money_transfer, name='money_transfer'),
    path('pay/wallet/<str:r_id>/', wallet_pay_success, name='wallet_pay_success'),

    path('pay/now/<int:pk>/', pay_now, name='pay_now'),
    path('my/payments/', PaymentView.as_view(), name='PaymentView'),
    path('success/payments/<int:user_id>/<str:unique_id>/',
         payment_success, name='payment_success'),
    path('failed/payments/', payment_failed, name='payment_failed'),

    path('cash/refound/', money_withdraw, name='money_withdraw'),
    path('wallet/cash/out/', wallet_withdraw, name='wallet_withdraw'),

    path('packages/', PackageView.as_view(), name='PackageView'),
    path('package/<int:pk>/edit/', edit_package, name='edit_package'),
    path('package/<int:pk>/delete/', delete_package, name='delete_package'),

    path('refer/price/', ReferPriceView.as_view(), name='ReferPriceView'),
    path('refer/price/<int:pk>/edit/', edit_refer_price, name='edit_refer_price'),
    path('refer/price/<int:pk>/delete/',
         delete_refer_price, name='delete_refer_price'),
    path('refer/history/', ReferHistoryView.as_view(), name='ReferHistoryView'),

    path('all/transactions/', AllTransactions.as_view(), name='AllTransactions'),
    path('api/today/transactions/', AllTodayTransactions.as_view(),
         name='AllTodayTransactions'),
    path('api/this/month/transactions/',
         AllThisMonthTransactions.as_view(), name='AllThisMonthTransactions'),
    path('api/date/transactions/', AllTransactionsDateFilter.as_view(),
         name='AllTransactionsDateFilter'),


    path('my/deliveries/finish/', FinishedView.as_view(), name="FinishedView"),
    path('my/deliveries/accept/', AcceptedView.as_view(), name="AcceptedView"),

    path('in/cash/collector/', in_cash_collection, name="in_cash_collection"),
    path('in/cash/collector/report/<int:collector>/',
         in_cash_collection_report, name="in_cash_collection_report"),
    path('in_cash/collection/report/delete/<int:pk>/',
         in_collection_delete, name="in_collection_delete"),
    path('in/cash/collection/report/delete/<int:pk>/',
         in_all_collection_delete, name="in_all_collection_delete"),
    path('in/today/cash/collection/',
         InTodayCollection.as_view(), name='TodayCollection'),
    path('in/month/cash/collection/',
         InThisMonthCollection.as_view(), name='ThisMonthCollection'),
    path('in/date/cash/collection/', InCashCollectionDateFilter.as_view(),
         name='CashCollectionDateFilter'),

    path('all/cash/collector/', all_cash_collection, name="all_cash_collection"),
    path('all/today/cash/collection/',
         AllTodayCollection.as_view(), name='AllTodayCollection'),
    path('all/month/cash/collection/', AllThisMonthCollection.as_view(),
         name='AllThisMonthCollection'),
    path('all/date/cash/collection/', AllCashCollectionDateFilter.as_view(),
         name='AllCashCollectionDateFilter'),

    path('create/faq/', CreateFAQ.as_view(), name="CreateFAQ"),
    path('app/faq/', HelpFAQS.as_view(), name="HelpFAQS"),
    path('booking/faq/', PrivacyFAQS.as_view(), name="PrivacyFAQS"),
    path('user/app/faq/', UserHelpFAQS.as_view(), name="UserHelpFAQS"),
    path('user/booking/faq/', UserPrivacyFAQS.as_view(), name="UserPrivacyFAQS"),
    path('faq/details/<int:pk>/', FAQDetails.as_view(), name="FAQDetails"),
    path('faq/update/<int:pk>/', FAQUpdate.as_view(), name="FAQUpdate"),
    path('faq/delete/<int:pk>/', FAQDelete.as_view(), name="FAQDelete"),

    path('set/prices/', SetPrices.as_view(), name="SetPrices"),
    path('price/', PriceList.as_view(), name="Price"),

    path('activate/<int:id>', activate, name='activate'),

    path('send_push/', send_push, name = 'send_push'),
    path('home/', home, name = 'home'),
    path('sw.js/', TemplateView.as_view(template_name='sw.js', content_type='application/x-javascript'))
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

# <i class="fab fa-adn"></i>
