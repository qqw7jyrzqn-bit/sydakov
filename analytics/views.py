"""
Views для аналитики и отчётов.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Avg
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta
from django.utils import timezone
import json

from wells.models import Well
from documents.models import Document
from accounts.mixins import head_pto_required


@login_required
@head_pto_required
def analytics_dashboard(request):
    """Главный дашборд аналитики (только для начальника ПТО)"""
    
    # Общая статистика
    total_wells = Well.objects.count()
    active_wells = Well.objects.filter(status='in_work').count()
    completed_wells = Well.objects.filter(status='completed').count()
    pending_approval = Well.objects.filter(status='submitted').count()
    
    # Статистика по месторождениям
    fields_stats = Well.objects.values('field').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Статистика по статусам
    status_stats = Well.objects.values('status').annotate(
        count=Count('id')
    )
    
    # Динамика создания скважин по месяцам (последние 12 месяцев)
    twelve_months_ago = timezone.now() - timedelta(days=365)
    wells_by_month = Well.objects.filter(
        created_at__gte=twelve_months_ago
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    # Средняя глубина скважин
    avg_depth = Well.objects.aggregate(avg_depth=Avg('depth'))['avg_depth'] or 0
    
    # Топ авторов
    top_authors = Well.objects.values(
        'author__first_name', 'author__last_name', 'author__username'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Статистика по документам
    total_documents = Document.objects.count()
    documents_by_type = Document.objects.values('document_type').annotate(
        count=Count('id')
    )
    
    # Подготовка данных для графиков
    months_labels = [item['month'].strftime('%b %Y') for item in wells_by_month]
    months_data = [item['count'] for item in wells_by_month]
    
    fields_labels = [item['field'] for item in fields_stats]
    fields_data = [item['count'] for item in fields_stats]
    
    status_labels = [dict(Well.STATUS_CHOICES).get(item['status'], item['status']) for item in status_stats]
    status_data = [item['count'] for item in status_stats]
    
    context = {
        'total_wells': total_wells,
        'active_wells': active_wells,
        'completed_wells': completed_wells,
        'pending_approval': pending_approval,
        'avg_depth': round(avg_depth, 2),
        'fields_stats': fields_stats,
        'top_authors': top_authors,
        'total_documents': total_documents,
        'documents_by_type': documents_by_type,
        
        # Данные для графиков (JSON)
        'months_labels': json.dumps(months_labels),
        'months_data': json.dumps(months_data),
        'fields_labels': json.dumps(fields_labels),
        'fields_data': json.dumps(fields_data),
        'status_labels': json.dumps(status_labels),
        'status_data': json.dumps(status_data),
    }
    
    return render(request, 'analytics/dashboard.html', context)


@login_required
@head_pto_required
def field_report(request, field_name):
    """Детальный отчёт по месторождению"""
    wells = Well.objects.filter(field=field_name)
    
    stats = {
        'total': wells.count(),
        'by_status': wells.values('status').annotate(count=Count('id')),
        'avg_depth': wells.aggregate(avg_depth=Avg('depth'))['avg_depth'] or 0,
        'total_depth': sum(float(w.depth) for w in wells),
    }
    
    context = {
        'field_name': field_name,
        'wells': wells,
        'stats': stats,
    }
    
    return render(request, 'analytics/field_report.html', context)


@login_required
@head_pto_required
def performance_report(request):
    """Отчёт по эффективности работы"""
    
    # Скважины по пользователям
    user_stats = Well.objects.values(
        'author__first_name', 'author__last_name', 'author__username', 'author__role'
    ).annotate(
        total=Count('id'),
        approved=Count('id', filter=Q(status='approved')),
        rejected=Count('id', filter=Q(status='rejected')),
        in_work=Count('id', filter=Q(status='in_work')),
    ).order_by('-total')
    
    # Время согласования
    from wells.models import ApprovalStep
    recent_approvals = ApprovalStep.objects.filter(
        status='approved',
        timestamp__gte=timezone.now() - timedelta(days=30)
    ).select_related('well', 'user')[:20]
    
    # Подсчитываем общие статистики
    total_created = sum(stat['total'] for stat in user_stats)
    total_approved = sum(stat['approved'] for stat in user_stats)
    total_rejected = sum(stat['rejected'] for stat in user_stats)
    
    context = {
        'user_stats': user_stats,
        'recent_approvals': recent_approvals,
        'total_created': total_created,
        'total_approved': total_approved,
        'total_rejected': total_rejected,
    }
    return render(request, 'analytics/performance_report.html', context)
