"""
URL configuration for bank project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from app_name import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),
    path('features', views.features, name='features'),
    path('Contact', views.Contact, name='Contact'),
    # path('About', views.about, name='About'),
    path('bot_iframe/', views.bot_iframe, name='bot_iframe'),
    # path('features/mutual_funds/', views.mutual_fund_recommendation, name='mutual_fund_recommendation'),
    path('mutual_funds/', views.mutual_fund_recommendation, name='mutual_funds'),
    path('loan_calculator_view/', views.loan_calculator_view, name='loan_calculator'),
    path('sip_calculator/', views.sip_calculator_view_web, name='sip_calculator'),
    path("dialogflow-webhook/", views.dialogflow_webhook, name="dialogflow_webhook"),

]    
