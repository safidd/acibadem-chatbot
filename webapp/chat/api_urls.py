from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.api_chat, name='api_chat'),
]