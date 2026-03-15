from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_page, name='chat'),
    path('health/', views.health_check, name='health'),
    
    path('api/chat/', views.api_chat, name='api_chat'),
]