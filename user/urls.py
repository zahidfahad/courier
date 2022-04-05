from django.urls import path, register_converter
from .views import *
from .decorators import forbidden
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.conf.urls import url
from django.contrib.auth import views

#url encoder
from user.utils import HashIdConverter
register_converter(HashIdConverter, "hashid")
#encoder ends

urlpatterns = [
    path('accounts/login/', views.LoginView.as_view(), name='login'),
    path('accounts/logout/', views.LogoutView.as_view(next_page='/'), name='logout'),

    # registration/activation
    path('register/', register, name='register'),
    path('user/registration/', user_registration, name='user_registration'),
    path('register/<int:pk>/', register_refer, name='register_refer'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('inactive/users/', acc_req_list, name='acc_req_list'),
    path('account/approval/<int:id>/', acc_approval, name='acc_approval'),

    # profiles
    path('my/profiles/', my_profile, name='my_profile'),
    path('profile/<hashid:id>/', profiles, name='profiles'),
    path('driver/profile/<hashid:id>/',
         driver_profile, name='driver_profile'),
    path('merchant/profile/<hashid:id>/',
         merchant_profile, name='merchant_profile'),
    path('agent/profile/<hashid:id>/',
         agent_profile, name='agent_profile'),
    path('delivery/man/profile/<hashid:id>/',
         delivery_man_profile, name='delivery_man_profile'),
    path('normal/user/profile/<hashid:id>/',
         user_profile, name='user_profile'),

    # msg
    path('msg/<int:id>/', user_msg, name='user_msg'),
    path('complain/<int:id>/', complain_box, name='complain_box'),
    path('complains', get_complains, name='get_complains'),
    path('delete/<int:id>/', delete_complains, name='delete_complains'),
    path('mark_read/<int:id>/', mark_as_read, name='mark_as_read'),


    # API
    path('get_complains', Get_complains.as_view()),
    path('comparing_monthly_diff/', Comparing_monthly_diff.as_view()),
    path('api/user/list/', user_list_view, name='UserListView'),
    path('updating/email/', Email_update.as_view()),
    path('notification/user/', User_notification.as_view()),


    # jsonresponses
    path('getting/status/', delivery_status_admin_profile,
         name='delivery_status_admin_profile'),


    # edit
    path('profile/edit/admin/<hashid:id>/',
         edit_profile_admin, name='edit_profile_admin'),
    path('driver/profile/edit/<hashid:id>/',
         edit_profile_driver, name='edit_profile_driver'),
    path('delivery/man/profile/edit/<hashid:id>/',
         edit_profile_delivery_man, name='edit_profile_delivery_man'),
    path('merchant/profile/edit/<hashid:id>/',
         edit_profile_merchant, name='edit_profile_merchant'),
    path('agent/profile/edit/<hashid:id>/',
         edit_profile_agent, name='edit_profile_agent'),
    path('user/profile/edit/<hashid:id>/',
         edit_profile_user, name='edit_profile_user'),

    # emailchange
    path('change/email/', change_email, name='change_email'),
    path('get_email/', get_email, name='get_email'),

    # visit
    path('profile/visit/gddg447dgdg414ddg1d<int:id>57dgd5d/',
         profile_visits, name='profile_visits'),

    # rate
    path('rate/', rate_user, name='rate_user'),
    path('ratings/', user_ratings, name='user_ratings'),

    # available
    path('available/<int:id>/', available, name='available'),

    # vehicle
    path('manage/vehicle/<hashid:id>/', vehicle_settings, name='vehicle_settings'),

    # password
    path('reset_password/',
         auth_views.PasswordResetView.as_view(
             template_name="user/password_reset.html"),
         name="reset_password"),

    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name="user/password_reset_sent.html"),
         name="password_reset_done"),

    # not responsive template
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name="user/password_reset_form.html"),
         name="password_reset_confirm"),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name="user/password_reset_done.html"),
         name="password_reset_complete"),

    path('changePass/', change_password, name='change_password'),

    path('<int:pk>/<str:ts>/', refer_cal, name='refer_cal'),
    path('create/refer/link/', create_refer_link, name='create_refer_link'),


    # search
    path('searching/', search_user, name='search_user'),
    path('searching2/', search_user2, name='search_user2'),
    path('searchingByadmin/', search_user3, name='search_user3'),
    path('search/results/', search_user4, name='search_user4'),
    path('autosuggest/', autosuggest, name='autosuggest'),
    path('agent/search/', search_agents, name='search_agents'),
    path('driver/search/', search_drivers, name='search_drivers'),


    # users
    path('users/', users, name='users'),

    # bar_chart
    path('monthly_order_history/', monthly_order_bar_chart,
         name='monthly_order_bar_chart'),

    # username_checker
    path('ajax/validate_username/', validate_username, name='validate_username'),

    # agent management
    path('managing/agents/', agent_list, name='agent_list'),
    path('agent/returned/deliveries/',
         return_deliveries, name='return_deliveries'),
    path('agent/on_the_way/deliveries/',
         delivering_deliveries, name='delivering_deliveries'),
    path('agent/pending/deliveries/',
         pending_deliveries, name='pending_deliveries'),
    path('agent/completed/deliveries/',
         complete_deliveries, name='complete_deliveries'),

    path('forbidden/access/', forbidden, name='forbidden'),
    path('agents/stats/dashboard/', agent_stats_dashboard,
         name='agent_stats_dashboard'),
    path('delete/agent/state/<int:id>/',
         delete_agent_stat, name='delete_agent_stat'),
    path('see/agents/complete/detail/<int:id>/',
         agents_order_detail, name='agents_order_detail'),

    # driver management
    path('driver/ratings/', driver_ratings, name='driver_ratings'),
    path('drivers/detail/', drivers_detail, name='drivers_detail'),
    path('driver/management/<hashid:id>/',
         driver_management, name="driver_management"),

    path('money/transfer/api/', MoneyTransferAPI.as_view(), name='MoneyTransferAPI'),
    path('user/activation/<int:id>/', user_activation, name='user_activation'),

    path('verifying/details/', email_redirect_view, name='email_redirect_view'),

     #inactive user msg login
    path('inactivity/', inactive_message, name='inactive_message'),
    path('payments/noti/api/', PaymentNotificationAPI.as_view(), name='PaymentNotificationAPI'),
    path('my/managed/commission/', MyCommissionAPI.as_view(), name='MyCommissionAPI'),
    path('query/', demo_animation, name='demo_animation'),
    path('user/dashboard/', user_dashboard, name='user_dashboard'),
    path('user/chart/order/', individual_order_chart_for_user, name='individual_order_chart_for_user'),
    path('user/complete/order/', individual_order_completed_user, name='individual_order_completed_user'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
