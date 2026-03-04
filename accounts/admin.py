"""
Административная панель для приложения accounts.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from .models_chat import ChatMessage


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Административная панель для кастомной модели User"""
    
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'company', 'is_active']
    list_filter = ['role', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'company']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('role', 'phone', 'company', 'signature'),
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': ('role', 'phone', 'company'),
        }),
    )


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """Административная панель для сообщений чата"""
    list_display = ['sender', 'recipient', 'message_preview', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at']
    search_fields = ['sender__username', 'recipient__username', 'message']
    readonly_fields = ['created_at', 'read_at']
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Сообщение'
