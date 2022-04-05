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
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.generic import CreateView, DetailView, UpdateView, ListView, DeleteView, TemplateView
from courier.serializers import CashCollectionSerializer
from django.contrib.auth.decorators import login_required
from .serializer import *
from user.models import Notification


class WalletAPIView(APIView):
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            user_id = self.request.user.id
            data =WalletModel.objects.filter(user=user_id)
            serializer = WalletModelSerializer(data=data, many=True)
            return Response(serializer, status= status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
