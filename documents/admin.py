"""
Административная панель для приложения documents.
"""
from django.contrib import admin
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Административная панель для модели Document"""
    
    list_display = ['title', 'well', 'document_type', 'uploaded_by', 'uploaded_at']
    list_filter = ['document_type', 'uploaded_at']
    search_fields = ['title', 'well__name', 'description']
    readonly_fields = ['uploaded_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('well', 'title', 'document_type'),
        }),
        ('Файлы', {
            'fields': ('file', 'generated_docx'),
        }),
        ('Дополнительно', {
            'fields': ('description', 'uploaded_by', 'uploaded_at'),
        }),
    )
