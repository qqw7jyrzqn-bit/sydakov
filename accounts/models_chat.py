"""
Модель чата/мессенджера между пользователями.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone


class ChatMessage(models.Model):
    """Сообщение в чате между пользователями"""
    
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name='Отправитель'
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_messages',
        verbose_name='Получатель'
    )
    message = models.TextField(verbose_name='Сообщение')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата отправки')
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')
    read_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата прочтения')
    
    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sender', 'recipient', '-created_at']),
            models.Index(fields=['recipient', 'is_read']),
        ]
    
    def __str__(self):
        return f'{self.sender.username} → {self.recipient.username}: {self.message[:50]}'
    
    def mark_as_read(self):
        """Отметить сообщение как прочитанное"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    @classmethod
    def get_conversation(cls, user1, user2):
        """Получить переписку между двумя пользователями"""
        return cls.objects.filter(
            models.Q(sender=user1, recipient=user2) |
            models.Q(sender=user2, recipient=user1)
        ).order_by('created_at')
    
    @classmethod
    def get_unread_count(cls, user):
        """Получить количество непрочитанных сообщений"""
        return cls.objects.filter(recipient=user, is_read=False).count()
    
    @classmethod
    def get_conversations_list(cls, user):
        """Получить список всех диалогов пользователя"""
        from django.db.models import Q, Max, Count
        
        # Находим всех собеседников
        sent_to = cls.objects.filter(sender=user).values_list('recipient', flat=True).distinct()
        received_from = cls.objects.filter(recipient=user).values_list('sender', flat=True).distinct()
        
        all_users = set(list(sent_to) + list(received_from))
        
        conversations = []
        for user_id in all_users:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            other_user = User.objects.get(pk=user_id)
            
            # Последнее сообщение
            last_msg = cls.objects.filter(
                Q(sender=user, recipient=other_user) |
                Q(sender=other_user, recipient=user)
            ).order_by('-created_at').first()
            
            # Непрочитанные от этого пользователя
            unread = cls.objects.filter(
                sender=other_user,
                recipient=user,
                is_read=False
            ).count()
            
            conversations.append({
                'user': other_user,
                'last_message': last_msg,
                'unread_count': unread
            })
        
        # Сортируем по дате последнего сообщения
        conversations.sort(key=lambda x: x['last_message'].created_at if x['last_message'] else timezone.now(), reverse=True)
        
        return conversations
