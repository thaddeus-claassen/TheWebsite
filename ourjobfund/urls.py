"""TheWebsite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url;
from django.contrib import admin;
from django.conf import settings;
from django.conf.urls.static import static;
from user.views import search_users;
from job.views import home;
from . import views;

app_name = 'ourjobfund';

urlpatterns = [
    url(r'search_users$', search_users),
    url(r'^admin/', admin.site.urls),
    url(r'^user/', include('user.urls')),
    url(r'^job/', include('job.urls')),
    url(r'^$', include('job.urls')),
    url(r'^jobuser/', include('jobuser.urls')),
    url(r'^info/', include('info.urls')),
    
] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT);
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT);
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

    
