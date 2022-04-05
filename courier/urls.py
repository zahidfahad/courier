from django.urls import path
from django.conf.urls import url
from .views import *
urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('driver/', driver_dashboard, name='driver_dashboard'),
    path('deliveryman/', deliveryman_dashboard, name='deliveryman_dashboard'),
    path('agent/', agent_dashboard, name='agent_dashboard'),
    path('merchant/', merchant_dashboard, name='merchant_dashboard'),
    path('api/driver/income/', DriverIncomeChart.as_view(),
         name='DriverIncomeChart'),

    path('create-order/', create_order, name="create_order"),
    path('order-list/', order_list, name="order_list"),
    path('order-<pk>/', OrderDetails.as_view(), name="order_details"),
    path('update-<pk>', OrderUpdate.as_view(), name="order_update"),
    path('cancel/order/<int:pk>', cancel_order, name="cancel_order"),
    path('status-update-<pk>', OrderStatusUpdate.as_view(),
         name="order_status_update"),
    path('<pk>-delete/', DeleteOrder.as_view(), name="delete_order"),

    path('change-pick-up-location/<int:id>/',
         change_pickup_location, name="change_pickup_location"),
    path('set/pickup/location/<int:id>/',
         set_pickup_location, name="set_pickup_location"),
    path('change-delivery-location/<int:id>/',
         change_delivery_location, name="change_delivery_location"),
    path('user-delivery-tracking/<int:id>/', user_delivery_tracking,
         name="user_delivery_tracking"),
    path('pick_up-locations/', pick_up_locations, name="pick_up_locations"),
    path('start-pick_up-user/<int:id>/', start_pickup, name='start_pick_up'),
    path('start-delivery/', start_delivery, name='start_delivery'),
    path('track-page/', track_page, name="track_page"),

    path('api/notification/', NotificationApi.as_view(), name='notification'),
    path('api/notification/length/', NotificationLengthApi.as_view(),
         name='notification_length'),
    path('api/user/notification/', UserNotification.as_view(),
         name='user_notification'),
    path('api/deliveryman/location/', DeliverymanLocation.as_view(),
         name='deliveryman_location'),
    path('api/notification/individual/', IndividualNotification.as_view(),
         name='individual_notification_api'),

    path('accept/<int:id>/', accept_user, name="accept_user"),
    path('approve/<int:id>/', approve_delivery_address_change,
         name="approve_change"),

    path('get/invoice/<int:pk>/', invoice_generator, name="invoice_generator"),


    path('order/complete/', CompletedReport.as_view(), name="CompletedReport"),
    path('order/delivering/', DeliveringReport.as_view(), name="DeliveringReport"),
    path('order/pending/', PendingReport.as_view(), name="PendingReport"),
    path('order/returned/', ReturnReport.as_view(), name="ReturnReport"),

    path('finish/<int:pk>/', finish_otp, name="finish_otp"),
    path('order/delivery<int:pk>/finish/',
         finish, name="confirm_order_delivery"),

    path('api/location/data/',
         change_location_data, name='change_location_data'),

    path('api/package/', PackagePriceAPI.as_view(), name='PackagePriceAPI'),

    path('manage/commission/', manage_commission, name='manage_commission'),
    path('manage/commission/<int:pk>/', manage_commission_seen,
         name='manage_commission_seen'),

    path('order/details/<int:pk>/', notification_order_details,
         name='notification_order_details'),
    path('user/track/<int:id>/', user_track, name="user_track"),
    path('user/track/driver/<int:id>/', user_track, name="user_track"),
    path('user/delivery/finish/<int:pk>/',
         details, name="details")

]
