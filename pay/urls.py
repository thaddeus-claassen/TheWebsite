from django.conf import settings;
from django.conf.urls import include, url;
from django.conf.urls.static import static;
from . import views;

app_name = 'pledge';

urlpatterns = [
    url(r'^(?P<pledge_random_string>[a-zA-Z0-9]+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^create/(?P<job_random_string>[a-zA-Z0-9]+)/$', views.CreateView.as_view(), name='create'),
    url(r'^confirmation/(?P<job_random_string>[a-zA-Z0-9]+)/$', views.payment_confirmation, name='confirmation'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT);
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT);