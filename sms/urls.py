# urls.py in the sms app

from django.urls import path
from . import views

app_name = 'sms'

urlpatterns = [
    path('compose/', views.compose_sms, name='compose_sms'),
    path('view/', views.view_sms, name='view_sms'),
]
