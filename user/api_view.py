from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from requests.api import request
from rest_framework import response
from rest_framework.generics import ListAPIView
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, viewsets
import json
from .serializers import *
from rest_framework.serializers import Serializer
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from Ecourier.settings import EMAIL_HOST_USER
from django.template.loader import render_to_string
from django.shortcuts import render, redirect, get_object_or_404
import datetime

def unique_code(id):
    date = datetime.datetime.now()
    timestamp = datetime.datetime.timestamp(date)
    code =  str(round(timestamp)) + str(-(id))
    return code

def verify_msg(request):
    return render(request, 'user/verified.html')



def noti_generator(request):
    context ={}
    code = ''
    data = ''
    if request.method == 'POST':
        code = request.POST.get('verification_code')
        try:
            data = User.objects.get(verification_code = code)
            if data.one_time_logic == 0:
                data.one_time_logic = 1
                data.save()
                Notification.objects.create(user_id=data.id, text='Email verified!', is_seen = False,
                                            is_activated = False)
                return redirect('verify_msg')
            else:
                return render(request,'user/expired.html',{'code': code})
        except:
            return render(request, 'user/user_not_found_with_given_code.html')
    context = {'code': code}
    return render(request,'user/code.html', context)
    

class MessageApi(APIView):
    def get(self, request):
        msg = Message.objects.all()
        serializer = ResponseMSGserializer(msg, many =True)
        return Response(serializer.data)

    def post(self, *args, **kwars):
        serializer = MessageSerializer(data = self.request.data)
        if serializer.is_valid(raise_exception =  True):
            serializer_2 = serializer.save()
            res_var = ResponseMSGserializer(serializer_2, many = False)
            return JsonResponse(res_var.data, status = status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors , status= status.HTTP_400_BAD_REQUEST)



def get_auth_token(pk):
    x=Token.objects.get(user=pk)
    dic = {'token': x.key}
    return dic

class LoginApi(viewsets.ViewSet):
    serializer_class = LoginSerializer
    authentication_classes = (TokenAuthentication, )
    @action(methods=['POST'], detail=False, )
    def login_view(self, request, pk=None):
        if request.data:
            us = request.data['username']
            ps = request.data['password']
            user = authenticate(request, username=us, password=ps)
            if user:
                login(request, user)
                data = User.objects.get(username=us)
                x = get_auth_token(data.id)
                return Response(x, status=status.HTTP_200_OK)
            else:
                Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class RegisterApi(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
            serializer = self.get_serializer(data = request.data)
            serializer.is_valid(raise_exception=True)
            username = serializer.validated_data.get('username')
            serializer.save()

            user = User.objects.get(username=username)
            user.is_active = False
            user.verification_code = unique_code(user.id)
            verification_code = user.verification_code
            user.save()

            current_site = get_current_site(request)
            mail_subject = 'Verify Your Email.'
            message = render_to_string('user/acc_active_email_api.html', {
                'user': user,
                'domain': current_site.domain,
                'link': current_site.domain,
                'code':  verification_code,
            })
            to_email = self.request.data['email']
            send_mail(mail_subject, message, EMAIL_HOST_USER, [to_email])

            token = get_auth_token(user.id)
            for k,v in token.items():
                if v:
                    token = v
            return Response({"token": token,"username": username,"id": user.id})


class AccountApproval(viewsets.ViewSet):
    serializer_class = AccountApprove

    @action(methods=['POST'], detail=False, )
    def approve_account(self, request, pk=None):
        if request.data:
            user = User.objects.get(username = request.data['username'])
            active = 'user is active already'
            username = user.username
            if user.is_active == False:
                try:
                    user.is_active = True
                    user.save()
                    to_mail = user.email
                    noti = Notification.objects.filter(
                        user = user, is_seen = False, is_activated = False)
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
                    acc_sts = user.is_active
                    send_mail(mail_subject, message, EMAIL_HOST_USER, [to_mail])
                    return Response({"Active": acc_sts, "Username": user.username, "Id": user.id})

                except:
                    return Response( status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response({"Active": active, "Username": username}, status = status.HTTP_405_METHOD_NOT_ALLOWED)

        else:
            return Response({"issue": "no user selected" }, status=status.HTTP_428_PRECONDITION_REQUIRED)
        