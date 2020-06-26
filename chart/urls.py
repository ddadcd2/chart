from django.urls import path

from .views import *
from chart import views
from django.conf.urls.static import static
from django.conf.urls import include, url
from django.conf import settings



app_name = 'chart'

urlpatterns = [
    path('', home, name='home'),
    path('ticket-class/3/',
         ticket_class_view_3, name='ticket_class_view_3'),
    path('covid-confirmed/', covid_confirmed, name='covid_confirmed'),
    path('covid-recovered/', covid_recovered, name='covid_recovered'),
    path('covid-deaths/', covid_deaths, name='covid_deaths'),

]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT)