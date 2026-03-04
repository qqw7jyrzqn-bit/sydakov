"""
Context processors для приложения notifications.
Добавляет непрочитанные уведомления в контекст всех шаблонов.
"""


def unread_notifications(request):
    """Добавляет непрочитанные уведомления в контекст"""
    if request.user.is_authenticated:
        return {
            'unread_notifications': request.user.notifications.filter(read=False)[:5],
            'unread_notifications_count': request.user.notifications.filter(read=False).count(),
        }
    return {
        'unread_notifications': [],
        'unread_notifications_count': 0,
    }
