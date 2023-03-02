from datetime import datetime, timedelta

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap  # new
from django.contrib.staticfiles.storage import staticfiles_storage
from django.shortcuts import redirect, render
from django.urls import include, path, re_path
from django.views.generic import TemplateView, base
from django.views.static import serve
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.views import get_schema_view
from rest_framework import permissions, routers
from Myapp import views
from rest_framework import routers, permissions
from django.conf import settings


if settings.DEBUG == True:
    router = routers.DefaultRouter()
    router.get_api_root_view().cls.__name__ = "Registre Dashboard"
    router.get_api_root_view().cls.__doc__  = "APIs Administrator Interface"
else:
    router = routers.SimpleRouter()
    
    
# router.register('User', views.UserViewSet           ,basename="User" )
# router.register('Actel', views.ActelViewSet         ,basename="Actel" )
# router.register('DOT', views.DOTViewSet             ,basename="DOT" )
router.register('Doleance', views.DoleanceViewSet   ,basename="Doleance" )
router.register('Regdor', views.RegdorViewSet   ,basename="RegDor" )

handler404 = views.Errorhandler404
handler500 = views.Errorhandler500

class PublicAPISchemeGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        schema.base_path = '/api/' # api/
        return schema

schema_view = get_schema_view(
   openapi.Info(
      title="Registre",
      swagger= "2.0",
      openapi = "2.0.0",
      default_version='V 1.0',
      description="Registre ENGINE",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="medchalouli@live.fr"),
      license=openapi.License(name="Registre License"),
      
    ),
    generator_class=PublicAPISchemeGenerator,
    # url='https://www.Registre.com/api/', # for Schemes as HTTPS
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('__debug__/', include('debug_toolbar.urls')),
    # SiteMap =================================================================================
    # path('sitemap.xml',sitemap,{'sitemaps': sitemaps}, name='sitemap'),
    path('login/', views.LoginPage,                     name="LoginPage"),      # Login
    path('api/GetActel/', views.GetActel.as_view(),     name="GetActel"), 
    path('api/GetCenter/', views.GetCenter.as_view(),   name="GetCenter"), 
    path('logout/', views.LogoutPage,                   name="LogoutPage"),     # LogOut
    path('admin/', include('admin_honeypot.urls',       namespace='admin_honeypot')),
    path('administrator/', admin.site.urls),                                    # Django Admin
    # Userpage ================================================================================
    
    path('api/loginWeb/',     views.LoginWebAPIView.as_view(),      name="loginWeb"),        

    path('',  views.IndexPage,                                      name="indexActel"),                                                  
    path('',  views.IndexPage,                                      name="indexDG"),                                                  
    path('',  views.IndexPage,                                      name="indexDO"),                                                  
    path('login/', views.LoginPage ,                                name="login"),        
    path('logout/', views.LogoutPage,                               name="LogoutPage"),  

    path('registre_stat/', views.RegistreStatPage,                  name="registre"), 
    path('registre_Or/', views.RegistreOrPage,                      name="Or"), 

    # APIs=======================================================================================
    path('api/', include(router.urls)),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('doc/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    
    path('favicon.ico', base.RedirectView.as_view(url=('/static/favicon.ico'))),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
] 
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL,  document_root=settings.MEDIA_ROOT)



