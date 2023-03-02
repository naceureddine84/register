
from django.contrib import admin,auth
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import Http404

from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.relations import PrimaryKeyRelatedField

from .models import  UserApp, LogUser, Doleance , DOT , Actel , Centre , Regdor

class DOTSerializer(serializers.ModelSerializer):

  class Meta:
    model = DOT
    fields = '__all__'

class ActelSerializer(serializers.ModelSerializer):

  class Meta:
    model = Actel
    fields = '__all__'
    
    # exclude = ( 'dot',)
  def to_representation(self, instance):
    rep = super().to_representation(instance)
    # DOT ================================================================
    rep['DOT_Code'] = DOTSerializer(instance.dot).data["code"]
    rep['DOT_Name'] = DOTSerializer(instance.dot).data["name"]
    return rep
class UserSerializer(serializers.ModelSerializer):
    # last_login = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S",required=False)
    def to_representation(self, instance):
      rep = super().to_representation(instance)
      # DOT ================================================================
      rep['Actel'] = ActelSerializer(instance.actel).data
      return rep
    class Meta:
        model = UserApp
        # fields = '__all__'
        exclude = ( 'groups', 'user_permissions','is_staff','is_superuser','is_active','date_joined','password','last_login','actel')

class DoleanceSerializer(serializers.ModelSerializer):
  regTypeName = serializers.CharField(source='get_regType_display',required=False,read_only=True)
  satisfyName = serializers.CharField(source='get_satisfy_display',required=False,read_only=True)
  statusName = serializers.CharField(source='get_status_display',required=False,read_only=True)
  dateCreate   = serializers.DateTimeField(format="%Y-%m-%d %H:%M",required=False)
  dateReview   = serializers.DateTimeField(format="%Y-%m-%d %H:%M",required=False)

  class Meta:
    model = Doleance
    fields = '__all__'
  def to_representation(self, instance):
    rep = super().to_representation(instance)
    # DOT ================================================================
    rep['AT_USER'] = UserSerializer(instance.userat).data
    rep['Actel'] = ActelSerializer(instance.actel).data
    
    return rep

class CentreSerializer(serializers.ModelSerializer):

  class Meta:
    model = Centre
    fields = '__all__'

class RegDorSerializer(serializers.ModelSerializer):
  dateCreate   = serializers.DateTimeField(format="%Y-%m-%d %H:%M",required=False)

  class Meta:
    model = Regdor
    fields = '__all__'
  def to_representation(self, instance):
    rep = super().to_representation(instance)
    # DOT ================================================================
    rep['USER'] = UserSerializer(instance.userat).data
    rep['Centre'] = CentreSerializer(instance.centre).data
    
    return rep

class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=255, min_length=2,)
    password = serializers.CharField(max_length=68, min_length=3, write_only=True)
    email = serializers.EmailField(max_length=150, read_only=True)

    class Meta:
        model = UserApp
        fields = ['username', 'password', 'email']

    def validate(self, attrs):
        username = attrs.get('username', '')
        password = attrs.get('password', '')

        user = auth.authenticate(username=username, password=password)
        if not user:
            raise AuthenticationFailed('Le nom d\'utilisateur ou le mot de passe est incorrect ')
        if not user.is_active:
            raise AuthenticationFailed('Compte désactivé, prière de contacter l\'administrateur!')
        
        return {
            'username': user.username,
            }

        return super().validate(attrs)

 