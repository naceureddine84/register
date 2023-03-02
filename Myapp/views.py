import json
import hashlib
import sys,os, re ,traceback ,base64, math
import time as functiontimer
from PIL import Image
from io import BytesIO
from os import mkdir, path, getcwd
from uuid import uuid4

from django.shortcuts import get_object_or_404
from django.conf import settings
from django.db import connection
from django.db.models import Count, DateField, Max,Min,Avg, Q ,Sum, F , Case , When , Value , IntegerField
from django.db.models.functions.datetime import ExtractMonth, TruncDate, TruncMonth
from django.forms.models import model_to_dict
from django.contrib.auth import authenticate, login
from django.contrib.sitemaps import Sitemap
# from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.serializers import serialize
from django.shortcuts import redirect, render , get_object_or_404
from django.http import JsonResponse, Http404, HttpResponse
from django.utils import timezone
from django.template import TemplateDoesNotExist
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django_filters import rest_framework as filters

from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import generics, status, views,viewsets
from rest_framework.permissions import IsAuthenticated

from itertools import chain, groupby
from datetime import datetime, timedelta, time

from .models import  UserApp, LogUser, Doleance, DOT, Actel , Regdor ,Centre
from .serializers import  UserSerializer ,DoleanceSerializer , DOTSerializer , ActelSerializer , RegDorSerializer , LoginSerializer, CentreSerializer , RegDorSerializer

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.views.decorators.cache import cache_page ,cache_control
from .renderers import UserRenderer
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages, auth
from django.template import loader
from django.http import JsonResponse, Http404, HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.http.response import HttpResponseServerError


def date_in_range(start, end, current):
    """Returns whether current is in the range [start, end]"""
    return start <= current <= end
# APIs ==========================================-------------------------------========================================
class UserViewSet(viewsets.ModelViewSet):
    queryset = UserApp.objects.all()
    serializer_class = UserSerializer
    # permission_classes = (IsAuthenticated, )
    http_method_names = ['get','post','patch','delete','head','option']

class RegdorViewSet(viewsets.ModelViewSet):
  http_method_names = ['get','post','patch','head','option']
  queryset = Regdor.objects.all()
  serializer_class = RegDorSerializer

  def get_queryset(self):
    queryset = self.queryset
    _user = self.request.query_params.get('User',"")
    _center    = self.request.query_params.get('Centre',0)
    _minDate  = self.request.query_params.get('minDate',"2022-01-01")
    _maxDate  = self.request.query_params.get('maxDate',"2024-01-01")

    if 'Centre' in self.request.query_params:
        queryset = queryset.filter(centre=_center)
    if 'minDate' in self.request.query_params and 'maxDate' in self.request.query_params:
            queryset = queryset.filter(	dateCreate__gte= _minDate,dateCreate__lte=_maxDate)
    return queryset.order_by("-id")
    
    def list(self, request, *args, **kwargs):
      queryset = self.get_queryset()
      
      serializerGet = RegDorSerializer(queryset, many=True)
      return Response(serializerGet.data)

class DoleanceViewSet(viewsets.ModelViewSet):
  http_method_names = ['get','post','patch','head','option']
  queryset = Doleance.objects.all()
  serializer_class = DoleanceSerializer

  def get_queryset(self):
    queryset = self.queryset
    _user = self.request.query_params.get('User',"")
    try:
      ATUser = get_object_or_404(UserApp , username = _user, role__in= [1,2,3])
      if (ATUser.role == 1) : queryset = queryset.select_related("actel").filter(actel = ATUser.actel)
      if (ATUser.role == 2) : queryset = queryset.select_related("actel").filter(actel__dot = ATUser.actel.dot)
      if (ATUser.role == 3) : queryset = queryset.select_related("actel").all()
    except Exception as ex: 
      print("Get Exception : ", ex)
        
    _status   = self.request.query_params.get('Status',0)
    _satisfy  = self.request.query_params.get('Satisfy',0)
    _type     = self.request.query_params.get('Type',0)
    _actel    = self.request.query_params.get('Actel',0)
    _dot      = self.request.query_params.get('DOT',0)
    _minDate  = self.request.query_params.get('minDate',"2022-01-01")
    _maxDate  = self.request.query_params.get('maxDate',"2024-01-01")

    if 'Status' in self.request.query_params:
        queryset = queryset.filter(status=_status)
    if 'Type' in self.request.query_params:
        queryset = queryset.filter(regType=_type)
    if 'Satisfy' in self.request.query_params:
        queryset = queryset.filter(satisfy=_satisfy)
    if 'Actel' in self.request.query_params:
        queryset = queryset.filter(actel_id=_actel)
    if 'DOT' in self.request.query_params:
        queryset = queryset.filter(actel__dot=_dot)
    if 'minDate' in self.request.query_params and 'maxDate' in self.request.query_params:
            queryset = queryset.filter(	dateCreate__gte= _minDate,dateCreate__lte=_maxDate)
    return queryset.order_by("-id")
    
    def list(self, request, *args, **kwargs):
      queryset = self.get_queryset()
      
      serializerGet = DoleanceSerializer(queryset, many=True)
      return Response(serializerGet.data)
class DOTViewSet(viewsets.ModelViewSet):
  queryset = DOT.objects.all()
  serializer_class = DOTSerializer
class ActelViewSet(viewsets.ModelViewSet):
  queryset = Actel.objects.all()
  serializer_class = ActelSerializer

credentials =openapi.Schema(
		type=openapi.TYPE_OBJECT,
		properties={ 'key': openapi.Schema(type=openapi.TYPE_STRING, description='key',example= "01:02:03:04:05:06"),})
class GetActel(generics.GenericAPIView):
    http_method_names = ['post','head','option']
    serializer_class = ActelSerializer
    
    @swagger_auto_schema(request_body=credentials)
    def post(self, request):
        try:
            keyid    = self.request.data['key']
            ActelQuery = Actel.objects.filter(keyid=keyid).first()
            if ActelQuery is not None:
              response = {    "Status": 1,
                              "code":     ActelQuery.code,
                              "name":     ActelQuery.name,
                              "name_ar":  ActelQuery.name_ar,
                              "type_actel":  ActelQuery.type_actel,
                              "DOT":      str(ActelQuery.dot),
                            }
            else:
              response = {    "Status": 0,
                              "Message": "Identificateur non valide",
                            }
            # Save a log about it:
            return JsonResponse(response)            
        except KeyError as e:
            print("KeyError : ",e)
            response = {     'Status' : 0 , 
                            'Message': " Erreur dans l\'input >> " + str(e)
                        }
            return Response(response,status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("Exception : ",e)
            response = {     'Status' : 0 , 
                            'Message': str(e)
                        }
            return Response(response,status=status.HTTP_200_OK) 

class GetCenter(generics.GenericAPIView):
    http_method_names = ['post','head','option']
    serializer_class = CentreSerializer
    
    @swagger_auto_schema(request_body=credentials)
    def post(self, request):
        try:
            keyid    = self.request.data['key']
            CentreQuery = Centre.objects.filter(keyid=keyid).first()
            if CentreQuery is not None:
              response = {    "Status": 1,
                              "code":   CentreQuery.code,
                              "name":   CentreQuery.name,
                              "name_ar":CentreQuery.name_ar,
                            }
            else:
              response = {    "Status": 0,
                              "Message": "Identificateur non valide",
                            }
            # Save a log about it:
            return JsonResponse(response)            
        except KeyError as e:
            print("KeyError : ",e)
            response = {     'Status' : 0 , 
                            'Message': " Erreur dans l\'input >> " + str(e)
                        }
            return Response(response,status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("Exception : ",e)
            response = {     'Status' : 0 , 
                            'Message': str(e)
                        }
            return Response(response,status=status.HTTP_200_OK) 

class LoginWebAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    http_method_names = ['get','post','head']
    renderer_classes = (UserRenderer,)
    
    def get(self, request):
        return redirect("/login/")
    def post(self, request):
      try:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_data = serializer.data
        user = UserApp.objects.get(username=user_data['username'])
        redirecturl = "Or"
        if user.role == 1: redirecturl = "indexActel"
        if user.role == 2: redirecturl = "indexDO"
        if user.role == 3: redirecturl = "indexDG"

        print(user_data['username']," =-= ",request.data['password'])

        if user is not None:
          login(request, user)
          userItem = authenticate(username=user_data['username'], password=request.data['password'])
          LogUser(username=userItem, ipadr=get_client_ip(request)).save() 
          # return HttpResponseRedirect(reverse('dashboardPage'))
          if 'next' in request.POST:
            return redirect( request.POST['next'])
          else:
            return redirect(reverse(redirecturl))
            
      except Exception as ex:
        print("Exception",ex)
        messages.warning(request, "Prière de vérifier vos coordonnées")
        return redirect("/login/")


# Common functions ===============================-------------------------------========================================
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
def LoginPage(request):
    if not request.user.is_anonymous:
        login(request, request.user)
        print("Welcome")
        return redirect("/")
    else:
        print('AnonymousUser')
    redirectLink = "/api/loginWeb/"
    return render(request, 'login.html',{ "link": redirectLink}   )
def LogoutPage(request):
    auth.logout(request)
    # messages.success(request, 'Merci pour votre visite!')
    return redirect('login')
def Errorhandler404(request, exception):
    myContext ={
      "exception" : "//{}{}".format(request.get_host() , request.path),
      }
    return render(request, '404.html', myContext, status=404)
def Errorhandler500(request,):
    exception_type, exception_object, exception_traceback = sys.exc_info()
    filename = exception_traceback.tb_frame.f_code.co_filename
    line_number = exception_traceback.tb_lineno
    myContext ={ "exception" : exception_object, }
    t = loader.get_template('500.html')
    type, value, tb = sys.exc_info()
    return HttpResponseServerError(t.render(myContext,request))
# User Pages =====================================-------------------------------========================================
@login_required(login_url="/login/")
def IndexPage(request): 
    ATUser = get_object_or_404(UserApp , username = request.user.username)
    templateLink = "dashboard.html"
    # if (ATUser.role == 1) :  templateLink = "dashboardDOT.html"
    # if (ATUser.role == 2) :  templateLink = "dashboardDOT.html"
    if (ATUser.role == 3) :  templateLink = "dashboardDG.html"
    
    try:
      if (ATUser.role == 1) : DoleanceQuery = Doleance.objects.select_related("actel").filter(actel = ATUser.actel)
      if (ATUser.role == 2) : DoleanceQuery = Doleance.objects.select_related("actel").filter(actel__dot = ATUser.actel.dot)
      if (ATUser.role == 3) : DoleanceQuery = Doleance.objects.select_related("actel").all()
      if (ATUser.role == 4) : return redirect(reverse('Or'))
      DoleanceQtt = len(DoleanceQuery)    
      # Chart 1=====================================================================
      status_names = [var[1] for var in Doleance.status.field.choices]
      CountState = DoleanceQuery.values("status").annotate(Count=Count('id'))
      Chart1_xAxis =  [var["Count"] for var in CountState]
      Chart1_yAxis = status_names
    # Chart 2=====================================================================
      type_names = [var[1] for var in Doleance.regType.field.choices]
      type_codes = [var[0] for var in Doleance.regType.field.choices]
      typeArray=[0,0,0]
      for item in DoleanceQuery:
        if   item.regType == type_codes[0] : typeArray[0]+=1 
        elif item.regType == type_codes[1] : typeArray[1]+=1 
        elif item.regType == type_codes[2] : typeArray[2]+=1 
      Chart2_xAxis= typeArray
      Chart2_yAxis= type_names
    # Chart 3=====================================================================
      satisfy_names = [var[1] for var in Doleance.satisfy.field.choices]
      satisfy_codes = [var[0] for var in Doleance.satisfy.field.choices]
      satisfyArray=[0,0,0]
      for item in DoleanceQuery:
        if   item.satisfy == type_codes[0] : satisfyArray[0]+=1 
        elif item.satisfy == type_codes[1] : satisfyArray[1]+=1 
        elif item.satisfy == type_codes[2] : satisfyArray[2]+=1 
      Chart3_xAxis= satisfyArray
      Chart3_yAxis= satisfy_names
    # Chart 4=====================================================================
      FlopQuery = Doleance.objects.select_related("actel").filter(status=0,actel__dot__isnull= False).values("actel__dot",).annotate(Count=Count('id')).order_by('-Count')
      dotArray   = []
      countArray = []
      
      for item in FlopQuery:
        dotArray.append(DOT.objects.get(code=item["actel__dot"]).name)
        countArray.append(item["Count"])
      Chart4_yAxis =  dotArray
      Chart4_xAxis =  countArray
    # END=====================================================================
    except Exception as e:
      print("Exception : ",e)
    myContext = {
        "MenuDash":"active",
        "Count_all": DoleanceQtt,
        
        # Chart 1=============================
        "Chart1_Title": "Etats",
        "Chart1_Desc" : "Etats des doléances globaux",
        "Chart1_xAxis": Chart1_xAxis,
        "Chart1_yAxis": Chart1_yAxis,
        # Chart 2=============================
        "Chart2_Title": "Types",
        "Chart2_Desc" : "Distribution des axes du registre de doléance",
        "Chart2_xAxis": Chart2_xAxis,
        "Chart2_yAxis": Chart2_yAxis,
        # Chart 3=============================
        "Chart3_Title": "Satisfaction",
        "Chart3_Desc" : "Distribution par satisfactions des clients",
        "Chart3_xAxis": Chart3_xAxis,
        "Chart3_yAxis": Chart3_yAxis,
        # Chart 4=============================
        "Chart4_Title": "FLOP",
        "Chart4_Desc" : "Directions ayant le plus de doléances non traités",
        "Chart4_xAxis": Chart4_xAxis,
        "Chart4_yAxis": Chart4_yAxis,
    }
    return render(request, templateLink , myContext)

@login_required(login_url="/login/")
def RegistreStatPage(request , Cmd=None):
    # (1, "Gestionnaire ACTEL"), (2, "Gestionnaire DOT"), (3, "Gestionnaire DG")
    ATUser = get_object_or_404(UserApp , username = request.user.username , role__in= [1,2,3])
    print(ATUser)
    # Parameters
    statusList  = [var for var in Doleance.status.field.choices]
    satisfyList = [var for var in Doleance.satisfy.field.choices]
    typeList    = [var for var in Doleance.regType.field.choices]
    # Table
    if (ATUser.role == 1) : 
        AgenceList = [ATUser.actel]
    if (ATUser.role == 2) : 
        # AgenceList = Actel.objects.filter(dot = ATUser.actel.dot) # All Actel of DO
        # Only with data inside
        ActelActive =  Doleance.objects.filter(actel__dot__isnull = ATUser.actel.dot).distinct("actel")
        AgenceList  =  Actel.objects.filter(code__in = [var.actel.code for var in ActelActive]).order_by("name")
    if (ATUser.role == 3) : 
        AgenceList = DOT.objects.all().order_by("name")
    
    
    myContext = {
        "MenuRegistreStat":"active",
        "statusList" : statusList,
        "satisfyList": satisfyList,
        "typeList"   : typeList,
        "AgenceList" : AgenceList,

        "AccessToken": ATUser.tokens()["access"],
        "Actel":ATUser.actel,
    }
    return render(request, 'registreStat.html', myContext)

@login_required(login_url="/login/")
def RegistreOrPage(request , Cmd=None):
    # (1, "Gestionnaire ACTEL"), (2, "Gestionnaire DOT"), (3, "Gestionnaire DG")
    ATUser = get_object_or_404(UserApp , username = request.user.username , role = 4)
    # Table
    AgenceList = Centre.objects.all().order_by("name")
    myContext = {
        "MenuRegistreOr":"active",
        "AgenceList" : AgenceList,

        "AccessToken": ATUser.tokens()["access"],
    }
    return render(request, 'registreOr.html', myContext)
