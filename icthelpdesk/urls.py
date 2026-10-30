from django.contrib import admin
from django.urls import path
from tickets import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.chat_pagina, name='chat_pagina'),
    path('api/chat/', views.chat_api, name='chat_api'),
]