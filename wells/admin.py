"""
Административная панель для приложения wells.
"""
from django.contrib import admin
from .models import Well, ApprovalStep
from .models_extended import Comment, Tag, WellHistory, WellDeadline, WellAttachment


class ApprovalStepInline(admin.TabularInline):
    """Inline для отображения шагов согласования"""
    model = ApprovalStep
    extra = 0
    readonly_fields = ['timestamp']


@admin.register(Well)
class WellAdmin(admin.ModelAdmin):
    """Административная панель для модели Well"""
    
    list_display = ['name', 'field', 'depth', 'status', 'author', 'created_at']
    list_filter = ['status', 'field', 'created_at']
    search_fields = ['name', 'field', 'description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ApprovalStepInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'field', 'coordinates', 'depth'),
        }),
        ('Статус и автор', {
            'fields': ('status', 'author'),
        }),
        ('Описание', {
            'fields': ('description',),
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(ApprovalStep)
class ApprovalStepAdmin(admin.ModelAdmin):
    """Административная панель для модели ApprovalStep"""
    
    list_display = ['well', 'user', 'status', 'timestamp']
    list_filter = ['status', 'timestamp']
    search_fields = ['well__name', 'user__username', 'comment']
    readonly_fields = ['timestamp']


# Регистрация расширенных моделей

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Административная панель для комментариев"""
    list_display = ['well', 'author', 'text_preview', 'parent', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['text', 'well__name', 'author__username']
    readonly_fields = ['created_at', 'updated_at']
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Текст комментария'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Административная панель для тегов"""
    list_display = ['name', 'color', 'description', 'created_by']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']


@admin.register(WellHistory)
class WellHistoryAdmin(admin.ModelAdmin):
    """Административная панель для истории скважин"""
    list_display = ['well', 'action', 'user', 'timestamp', 'ip_address']
    list_filter = ['action', 'timestamp']
    search_fields = ['well__name', 'user__username', 'comment']
    readonly_fields = ['timestamp']


@admin.register(WellDeadline)
class WellDeadlineAdmin(admin.ModelAdmin):
    """Административная панель для дедлайнов"""
    list_display = ['well', 'milestone', 'planned_date', 'actual_date', 'responsible', 'is_overdue']
    list_filter = ['milestone', 'planned_date']
    search_fields = ['well__name', 'responsible__username', 'notes']
    readonly_fields = ['created_at']
    
    def is_overdue(self, obj):
        return obj.is_overdue
    is_overdue.boolean = True
    is_overdue.short_description = 'Просрочено'


@admin.register(WellAttachment)
class WellAttachmentAdmin(admin.ModelAdmin):
    """Административная панель для вложений"""
    list_display = ['well', 'title', 'category', 'file_size_mb', 'uploaded_by', 'uploaded_at']
    list_filter = ['category', 'uploaded_at']
    search_fields = ['title', 'well__name', 'uploaded_by__username']
    readonly_fields = ['uploaded_at', 'file_size']
