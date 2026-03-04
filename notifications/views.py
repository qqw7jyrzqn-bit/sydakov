"""
Views для приложения notifications.
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Notification


@login_required
def notification_list(request):
    """Список уведомлений пользователя"""
    notifications = request.user.notifications.all()
    
    return render(request, 'notifications/notification_list.html', {
        'notifications': notifications,
    })


@login_required
@require_POST
def mark_as_read(request, pk):
    """Пометить уведомление как прочитанное (AJAX)"""
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.mark_as_read()
    
    return JsonResponse({
        'success': True,
        'unread_count': request.user.notifications.filter(read=False).count()
    })


@login_required
@require_POST
def mark_all_as_read(request):
    """Пометить все уведомления как прочитанные"""
    request.user.notifications.filter(read=False).update(read=True)
    
    return JsonResponse({
        'success': True,
        'unread_count': 0
    })
