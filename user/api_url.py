from os import name
from django.urls import path, include
from .api_view import *
from .decorators import forbidden
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.conf.urls import url
from django.contrib.auth import views
from rest_framework import routers


router=routers.DefaultRouter()
router.register('login', LoginApi, basename='login_api')
router.register('approval', AccountApproval, basename='approval_api')

urlpatterns = [
    path('api/message/', MessageApi.as_view(), name = 'msg'),
    path('api/verification/', verify_msg, name = 'verify_msg'),
    path('api/register/', RegisterApi.as_view(), name = 'mobile_register'),
    path('code/', noti_generator, name = 'noti_generator'),
    path('api/', include(router.urls) )
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
