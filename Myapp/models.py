import os
import re
from datetime import date, datetime, time, timedelta

from django.conf import settings
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.core.files.storage import FileSystemStorage
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg, Count, DateField, F, Max, Min, Q, Sum
# from django.db.models.manager import EmptyManager
from django.template.defaultfilters import truncatechars
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from application.validators import validate_file_extension
from . import functions as Myfunctions

class Centre(models.Model):
  code  = models.IntegerField(null=False,blank=False,primary_key=True) 
  name  = models.CharField(max_length=200,null=False,blank=False)
  name_ar = models.CharField(max_length=200,null=True,blank=True,default="")
  keyid = models.CharField(max_length=200,null=False,default="-",unique=False)

  def __str__(self):
    return self.name

  class Meta:
    db_table = 'centre'
    managed = True
    verbose_name = 'Structure'
    verbose_name_plural = 'Structures d\'OR'
# ACTEL : =================================================================================================
class DOT(models.Model):
  code = models.IntegerField(null=False,blank=False,primary_key=True) 
  name = models.CharField(max_length=200,null=False,blank=False)

  def __str__(self):
    return self.name

  class Meta:
    db_table = 'dot'
    managed = True
    verbose_name = 'DOT'
    verbose_name_plural = 'DO Telecoms'
class Actel(models.Model):
  code = models.AutoField(primary_key=True)
  name = models.CharField(max_length=200,null=False,blank=False)
  name_ar = models.CharField(max_length=200,null=True,blank=True,default="")
  keyid = models.CharField(max_length=200,null=False,default="",unique=False)
  type_actel = models.CharField(max_length=50,null=True,blank=True)
  dot  = models.ForeignKey(DOT, on_delete=models.CASCADE, related_name="AttachedDOT")

  def __str__(self):
    return self.name + " [" + str(self.dot) + "]"

  class Meta:
    db_table = 'actel'
    managed = True
    verbose_name = 'Actel'
    verbose_name_plural = 'Actels'
# User Management : =========================================================================================
class UserManager(BaseUserManager):
    def create_user(self , _username, _fullname, _email, _password=None):
        if _username is None or _username == "":
            raise TypeError("Please introduice your username.")
        if _fullname is None:
            raise TypeError("Please introduice your fullname")
        if _email is None:
            raise TypeError("Please introduice your mail")
        
          
        user = self.model(
            username=_username,
            fullname=_fullname,
            email=_email,
            is_active = True
        )
        user.set_password(_password)
        user.save(using=self._db)
        return user
    def create_superuser(self,username,password):
        if password is None:
            raise TypeError("Le mot de passe ne doit pas être vide!")
        user = self.create_user(username, "SuperUSer Account",username+"@at.dz", password)
        user.is_active = True
        user.is_superuser = True
        user.is_verified = True
        user.is_staff = True
        user.save(using=self._db)
        return user
class UserApp(AbstractBaseUser, PermissionsMixin):  # To add Group and permissions
    username = models.CharField(max_length=150,blank=False,unique=True,primary_key=True, verbose_name="Nom d'utilisateur")
    email   = models.EmailField(max_length=150,null=False,blank=False,unique=True, verbose_name="e-mail")
    mobile  = models.CharField(max_length=150,null=False,blank=False, verbose_name="Numéro de téléphone")

    password = models.CharField(max_length=150,blank=False,null=False, verbose_name="Mot de passe")
    fullname = models.CharField(max_length=150,null=False, verbose_name="Nom complet")
    actel    = models.ForeignKey(Actel, on_delete=models.SET_NULL,null=True, blank=True, related_name="ACTEL")

    roleList = ((0, "Administrateur"),(1, "Gestionnaire ACTEL"), (2, "Gestionnaire DOT"), (3, "Gestionnaire DG"), (4, "Gestionnaire OR"))
    role     = models.SmallIntegerField(default=0,choices=roleList)
    

    date_joined = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    last_login  = models.DateTimeField(auto_now=True, blank=True, null=True)
    
    is_staff    = models.BooleanField(default=False)
    is_superuser= models.BooleanField(default=False)
    is_active   = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=True)
    
    USERNAME_FIELD = "username"
    # REQUIRED_FIELDS = []
    objects = UserManager()

    class Meta:
        db_table = "myusers"
        managed = True
        verbose_name = "User"
        verbose_name_plural = "Users"
    
    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)}
        
    def __str__(self):
        return "{}".format(self.email)

    def get_full_name(self):
        return self.fullname

    def get_short_name(self):
        return self.username

    @property
    def is_admin(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_staff
 
class LogUser(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.ForeignKey(UserApp, verbose_name="Username", on_delete=models.CASCADE , related_name="+")
    dateLog = models.DateTimeField(auto_now_add=True,verbose_name="Logging Date")
    ipadr = models.CharField(max_length=100,default="-",verbose_name="IP Address")
    # model_icons = "nav-icon fas fa-users"
    def __str__(self):
        return "{} : {}".format(self.username, self.dateLog )
        # def NewField(self):
        #     return f"{self.username.fullname}:{self.dateLog}"
    def save(self, *args, **kwargs):
        # super(LogUser, self).save(*args, **kwargs) # This will trigger saving
        return super(LogUser, self).save(*args, **kwargs)
    class Meta:
        db_table = 'logs'
        managed = True
        verbose_name = 'log'
        verbose_name_plural = 'logs'
# Database : ================================================================================================
class Doleance(models.Model):
  typeList    = ((0, "Appréciation positive"),(1, "Suggestions /Remareques"),(2, "Doléances"))
  satisfyList = ((0, "Négative"),(1, "Neutre"),(2, "Positive"))
  satatusList = ((0, "En cours de traitement"),(1, "Traitée"))
  dateCreate  = models.DateTimeField(auto_now_add=True)
  contenu     = models.ImageField(upload_to="clientpic/", null=True, blank=True,)
  actel       = models.ForeignKey(Actel, on_delete=models.SET_NULL, null=True, related_name="Doleance")
  regType     = models.SmallIntegerField(default=0, choices=typeList ,validators=[MaxValueValidator(2),MinValueValidator(0)], verbose_name="Type")
  satisfy     = models.SmallIntegerField(default=1, choices=satisfyList ,validators=[MaxValueValidator(2),MinValueValidator(0)], verbose_name="Satisfaction")
  userat      = models.ForeignKey(UserApp, verbose_name="Utilisateur", on_delete=models.SET_NULL, related_name="+" , null=True, blank=True)
  dateReview  = models.DateTimeField(auto_now = True,null=True,blank=True)
  status      = models.SmallIntegerField(default=0, choices=satatusList ,validators=[MaxValueValidator(1),MinValueValidator(0)], verbose_name="Etat")
  comment     = models.TextField(null=True,blank=True, verbose_name="Commantaire",)
  
  def __str__(self):
    return  self.get_regType_display() + " : " + self.get_satisfy_display()

  class Meta:
    db_table = 'doleance'
    managed = True
    verbose_name = 'Doleance'
    verbose_name_plural = 'Doleances'

        
class Regdor(models.Model):
  dateCreate  = models.DateTimeField(auto_now_add=True)
  contenu     = models.ImageField(upload_to="regdorpic/", null=True, blank=True,)
  dateReview  = models.DateTimeField(auto_now = True,null=True,blank=True)
  centre      = models.ForeignKey(Centre, on_delete=models.SET_NULL, null=True, related_name="+")
  comment     = models.CharField(max_length=250,null=True,blank=True, verbose_name="Observation",)
  userat      = models.ForeignKey(UserApp, verbose_name="Utilisateur", on_delete=models.SET_NULL, related_name="+" , null=True, blank=True)
  
  
  def __str__(self):
    return  str(self.dateCreate)

  class Meta:
    db_table = 'regdor'
    managed = True
    verbose_name = 'appreciation'
    verbose_name_plural = 'Registre d\'Or'