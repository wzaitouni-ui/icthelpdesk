from django.contrib import admin
from django.urls import path
from tickets import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.chat_pagina, name='home'),
    path('api/tickets/', views.ticket_aanmaken, name='ticket_aanmaken'),
]