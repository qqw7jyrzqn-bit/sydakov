"""
Views для мессенджера.
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models_chat import ChatMessage

User = get_user_model()


@login_required
@require_http_methods(["GET"])
def get_users_list(request):
    """Получить список пользователей для начала чата"""
    search = request.GET.get('search', '')
    
    users = User.objects.exclude(id=request.user.id).filter(
        Q(username__icontains=search) |
        Q(first_name__icontains=search) |
        Q(last_name__icontains=search)
    )[:10]
    
    users_data = [{
        'id': user.id,
        'username': user.username,
        'full_name': user.get_full_name() or user.username,
        'role': user.get_role_display() if hasattr(user, 'role') else 'Пользователь'
    } for user in users]
    
    return JsonResponse({'users': users_data})


@login_required
@require_http_methods(["GET"])
def get_conversations(request):
    """Получить список всех диалогов"""
    conversations = ChatMessage.get_conversations_list(request.user)
    
    conversations_data = [{
        'user_id': conv['user'].id,
        'username': conv['user'].username,
        'full_name': conv['user'].get_full_name() or conv['user'].username,
        'last_message': conv['last_message'].message[:50] if conv['last_message'] else '',
        'last_message_time': conv['last_message'].created_at.strftime('%d.%m.%Y %H:%M') if conv['last_message'] else '',
        'unread_count': conv['unread_count']
    } for conv in conversations]
    
    return JsonResponse({'conversations': conversations_data})


@login_required
@require_http_methods(["GET"])
def get_messages(request, user_id):
    """Получить сообщения с конкретным пользователем"""
    other_user = get_object_or_404(User, pk=user_id)
    
    messages = ChatMessage.get_conversation(request.user, other_user)
    
    # Отмечаем входящие сообщения как прочитанные
    unread_messages = messages.filter(recipient=request.user, is_read=False)
    for msg in unread_messages:
        msg.mark_as_read()
    
    messages_data = [{
        'id': msg.id,
        'sender_id': msg.sender.id,
        'sender_name': msg.sender.get_full_name() or msg.sender.username,
        'message': msg.message,
        'created_at': msg.created_at.strftime('%d.%m.%Y %H:%M'),
        'is_mine': msg.sender == request.user,
        'is_read': msg.is_read
    } for msg in messages]
    
    return JsonResponse({
        'messages': messages_data,
        'other_user': {
            'id': other_user.id,
            'username': other_user.username,
            'full_name': other_user.get_full_name() or other_user.username
        }
    })


@login_required
@require_http_methods(["POST"])
def send_message(request):
    """Отправить сообщение"""
    import json
    
    data = json.loads(request.body)
    recipient_id = data.get('recipient_id')
    message_text = data.get('message', '').strip()
    
    if not recipient_id or not message_text:
        return JsonResponse({'error': 'Не указан получатель или текст сообщения'}, status=400)
    
    recipient = get_object_or_404(User, pk=recipient_id)
    
    if recipient == request.user:
        return JsonResponse({'error': 'Нельзя отправить сообщение самому себе'}, status=400)
    
    # Создаём сообщение
    message = ChatMessage.objects.create(
        sender=request.user,
        recipient=recipient,
        message=message_text
    )
    
    # Создаём уведомление для получателя
    from notifications.models import Notification
    Notification.objects.create(
        recipient=recipient,
        text=f'Новое сообщение от {request.user.get_full_name() or request.user.username}: {message_text[:50]}'
    )
    
    return JsonResponse({
        'success': True,
        'message': {
            'id': message.id,
            'sender_id': message.sender.id,
            'sender_name': message.sender.get_full_name() or message.sender.username,
            'message': message.message,
            'created_at': message.created_at.strftime('%d.%m.%Y %H:%M'),
            'is_mine': True
        }
    })


@login_required
@require_http_methods(["GET"])
def get_unread_count(request):
    """Получить количество непрочитанных сообщений"""
    count = ChatMessage.get_unread_count(request.user)
    return JsonResponse({'unread_count': count})
