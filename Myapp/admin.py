from django.contrib import admin
from . import models
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django import forms
from django.utils.html import format_html
from django.db.models import Count, DateField, Max,Min,Avg, Q ,Sum, F
from import_export import resources, widgets
from import_export.admin import ExportActionMixin, ImportExportModelAdmin
from import_export.fields import Field
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter, NumericRangeFilter
from datetime import datetime

import os
admin.site.site_header = "Registre Admin"
admin.site.site_title = "Registre Admin Portal"
admin.site.index_title = "Welcome to Registre Portal"

# Actions ==============================================================================================
class LogUserResource(resources.ModelResource):
    
    User_name   = Field( column_name='Username',    attribute='username__username',   )
    User_email  = Field( column_name='E-mail',      attribute='username__email',   )
    User_role   = Field( column_name='Role ID' ,    attribute='username__role',   )
    ipAdr       = Field( column_name='IP Address' , attribute='ipadr',  )
    is_Staff    = Field( column_name="Permissions", readonly=True )

    def dehydrate_is_Staff(self, LogUser):
        userID = getattr(LogUser, "username", "-")
        theUser= models.UserApp.objects.get(username=userID.username)
        return 'Superuser: %s - Staff: %s' % (theUser.is_superuser, theUser.is_staff)
    class Meta:
        from_encoding = "utf-8-sig"
        model = models.LogUser
        fields = ('id','User_name', 'User_email','User_role' ,'dateLog','ipAdr','is_Staff')
        import_id_fields = ('id',)
        # exclude = ("User_email","User_role","is_Staff")
        export_order = fields
        
        #  Importation ===============
        # skip_unchanged = True
# class OrderDetailsButton(ImportExportModelAdmin):
#     resource_classes = [OrderDetailsResource]

@admin.action(description='Mark selected stories as published')
def make_published(modeladmin, request, queryset):
    queryset.update(status=True)
@admin.action(description=' Copy selected items')   

def duplicate_event(modeladmin, request, queryset):
    for object in queryset:
        object.id = None
        object.save()

duplicate_event.short_description = "Duplicate selected record"
# User Admin ============================================================================================

class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """
    password = ReadOnlyPasswordHashField(
        help_text= ("Raw passwords are not stored, so there is no way to see "
                    "this user's password, but you can change the password "
                    "using  this button <input type='button' onclick='location.href=\"../password/\";'value='Change Password' />."))
    class Meta:
        model = models.UserApp
        fields = '__all__'

    def clean_password(self):
        return self.initial["password"]
@admin.register(models.UserApp)
class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display =  ('username','password', 'fullname' ,'email' ,'role', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('is_staff','is_active',)
    prepopulated_fields = {'email': ('username',),}
    add_fieldsets = (
        ('Utilisateur ',  {'fields': ('username','password1','password2','fullname','email',)}),
        ('Attachement ',    {'fields': ('mobile','role','actel',)}),)
    
    # lookup_field = 'id'
    fieldsets = (
        (None, {'fields': ('username','email','password')}),
        ('Personal info', {'fields': ('fullname','role','actel')}),
        ('Permissions', {'fields': ('is_active','is_staff')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    
    # readonly_fields =('last_login',)
    search_fields = ('username', 'fullname')
    ordering = ('fullname',)
    filter_horizontal = ()
    actions = [duplicate_event]
    # admin.site.unregister(Group)

@admin.register(models.LogUser)
class LogUserAdmin(ImportExportModelAdmin,):
    myFields= [field.name for field in models.LogUser._meta.get_fields()]
    # myFields.remove('is_staff')
    list_display=myFields
    date_hierarchy = 'dateLog'
    search_fields = ('username.fullname',)
    list_filter = ('username','ipadr',)
    # list_filter = ('username','ipadr',('dateLog', DateRangeFilter))
    # filter_horizontal = ()
    actions = [duplicate_event]
    resource_classes = [LogUserResource]    
    # Date Range:---------------------------------------------------------------------------------
    # If you would like to add a default range filter
    # method pattern "get_rangefilter_{field_name}_default"
    def get_rangefilter_dateLog_default(self, request):
        return (datetime.today, datetime.today)

    # If you would like to change a title range filter method pattern "get_rangefilter_{field_name}_title"
    # def get_rangefilter_dateLog_title(self, request, field_path):
        # return 'Date Range Filter!'

class ActelStackedAdmin(admin.TabularInline):
    model = models.Actel
    readonly_fields = ('code',)

class DoleanceStackedAdmin(admin.TabularInline):
    model = models.Doleance

@admin.register(models.DOT)
class DotAdmin(admin.ModelAdmin):
    list_display= ['code','name']
    inlines = [ActelStackedAdmin,]
    list_filter = ('name','code',)

@admin.register(models.Centre)
class CentreAdmin(admin.ModelAdmin):
    list_display= ['code','name']
    list_filter = ('name','code',)
    
# @admin.register(models.Actel)
class ActelAdmin(admin.ModelAdmin):
    list_display= ['code','name','type_actel','keyid','dot']    
    inlines = [DoleanceStackedAdmin,]
    
@admin.register(models.Doleance)
class DoleanceAdmin(admin.ModelAdmin):
    def image(self, obj):
        try:
          return format_html('<img src="{}" class ="img-thumbnail img-rounded" width="50px" height="50px" />'.format(obj.contenu.url))
        except:
          return format_html('<img src="/static/vendor/adminlte/img/AdminLTELogo.png" width="50px" height="50px" />')
    def delete_button(self, obj):
      return format_html('<a class="btn btn-danger" href="/administrator/Myapp/doleance/{}/delete/">Delete</a>', obj.id)

    # def get_queryset(self, request):
    #     print(request.user.actel.code)
    #     query = super(DoleanceAdmin, self).get_queryset(request)
    #     filtered_query = query.filter(actel_id=request.user.actel.code)
    #     return filtered_query

    fields1= [field.name for field in models.Doleance._meta.get_fields()]
    fields1.remove('contenu')
    fields1.remove('comment')
    # fields1.remove('actel')
    fields1.append('image')
    fields1.append('delete_button')
    list_display= fields1
    # list_editable = ("status",)
    list_display_links = ["id",]
    # IF not superuser
    readonly_fields = ("image", "dateReview","userat",)
    list_filter = ('satisfy','regType','status','userat','actel','actel__dot')
    date_hierarchy = 'dateCreate'
    actions = [duplicate_event]
    

@admin.register(models.Regdor)
class RegdorAdmin(admin.ModelAdmin):
    def image(self, obj):
        try:
          return format_html('<img src="{}" class ="img-thumbnail img-rounded" width="50px" height="50px" />'.format(obj.contenu.url))
        except:
          return format_html('<img src="/static/vendor/adminlte/img/AdminLTELogo.png" width="50px" height="50px" />')
    def delete_button(self, obj):
      return format_html('<a class="btn btn-danger" href="/administrator/Myapp/regdor/{}/delete/">Delete</a>', obj.id)

    fields1= [field.name for field in models.Regdor._meta.get_fields()]
    fields1.remove('contenu')
    fields1.append('image')
    fields1.append('delete_button')
    list_display= fields1
    # list_editable = ("status",)
    list_display_links = ["id",]
    # IF not superuser
    readonly_fields = ("image",)
    list_filter = ('dateCreate',)
    date_hierarchy = 'dateCreate'
    
    # =-=-=-=-=-=-=-=-=-=-=-==-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    class CustomAdminSite(admin.AdminSite):

      def index(self, request, extra_context=None):
          extra_context = extra_context or {}
          extra_context['foo'] = 'bar'
          return super().index(request, extra_context=extra_context)
    # =-=-=-=-=-=-=-=-=-=-=-==-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    