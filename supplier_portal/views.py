"""
Views для приложения supplier_portal.
Специальный портал для поставщиков с ограниченным доступом.
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from accounts.mixins import SupplierRequiredMixin
from django.views.generic import ListView
from documents.models import Document
from wells.models import Well


@login_required
def supplier_dashboard(request):
    """Дашборд для поставщиков"""
    if not request.user.is_supplier():
        return HttpResponseForbidden("Доступ запрещён. Эта страница только для поставщиков.")
    
    # Поставщик видит только документы типа "Техническое задание"
    documents = Document.objects.filter(
        document_type='technical_spec'
    ).select_related('well', 'uploaded_by')
    
    return render(request, 'supplier_portal/dashboard.html', {
        'documents': documents,
    })


@login_required
def supplier_document_detail(request, pk):
    """Детальная информация о документе для поставщика"""
    if not request.user.is_supplier():
        return HttpResponseForbidden("Доступ запрещён.")
    
    document = get_object_or_404(
        Document.objects.filter(document_type='technical_spec'),
        pk=pk
    )
    
    return render(request, 'supplier_portal/document_detail.html', {
        'document': document,
    })


@login_required
def supplier_upload_report(request, document_id):
    """Загрузка отчёта поставщиком"""
    if not request.user.is_supplier():
        return HttpResponseForbidden("Доступ запрещён.")
    
    # TODO: Реализовать загрузку PDF-отчётов поставщиками
    # Форма для загрузки файла
    
    return render(request, 'supplier_portal/upload_report.html', {
        'document_id': document_id,
    })
