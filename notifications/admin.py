"""
Административная панель для приложения notifications.
"""
from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Административная панель для модели Notification"""
    
    list_display = ['recipient', 'text_short', 'read', 'created_at']
    list_filter = ['read', 'created_at']
    search_fields = ['recipient__username', 'text']
    readonly_fields = ['created_at']
    
    def text_short(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_short.short_description = 'Текст'
