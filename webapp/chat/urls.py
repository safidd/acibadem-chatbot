from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_page, name='chat'),
    path('health/', views.health_check, name='health'),
    path('api/chat/', views.api_chat, name='api_chat'),
    path('api/rate/<int:message_id>/', views.rate_message, name='rate_message'),
    path('api/favorites/', views.get_favorites, name='get_favorites'),
]