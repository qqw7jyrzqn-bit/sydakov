"""
URL-маршруты для приложения accounts.
"""
from django.urls import path
from . import views
from . import views_chat

app_name = 'accounts'

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    
    # Chat/Messenger endpoints
    path('chat/users/', views_chat.get_users_list, name='chat_users'),
    path('chat/conversations/', views_chat.get_conversations, name='chat_conversations'),
    path('chat/messages/<int:user_id>/', views_chat.get_messages, name='chat_messages'),
    path('chat/send/', views_chat.send_message, name='chat_send'),
    path('chat/unread/', views_chat.get_unread_count, name='chat_unread'),
]
