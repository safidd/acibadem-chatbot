from django.urls import path
from . import views, api_views 

urlpatterns = [
    # Team's Standard Web Routes
    path('', views.chat_page, name='chat'),
    path('health/', views.health_check, name='health'),
    path('api/rate/<int:message_id>/', views.rate_message, name='rate_message'),
    
    # Week 9: Our new, fully functional API routes
    path('api/chat/', api_views.chat_endpoint, name='chat_endpoint'),
    path('api/favorites/', api_views.favorites_endpoint, name='favorites_endpoint'),
] 