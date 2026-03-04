"""
Модели приложения notifications.
Система уведомлений для пользователей.
"""
from django.db import models
from django.conf import settings
from django.core.mail import send_mail


class Notification(models.Model):
    """
    Модель уведомления.
    Поддерживает как in-app, так и email уведомления.
    """
    
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Получатель'
    )
    text = models.TextField(
        verbose_name='Текст уведомления'
    )
    read = models.BooleanField(
        default=False,
        verbose_name='Прочитано'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    well = models.ForeignKey(
        'wells.Well',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        verbose_name='Скважина'
    )
    
    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ['-created_at']
    
    def __str__(self):
        status = "✓" if self.read else "✗"
        return f"{status} {self.recipient.username}: {self.text[:50]}"
    
    def mark_as_read(self):
        """Пометить уведомление как прочитанное"""
        if not self.read:
            self.read = True
            self.save(update_fields=['read'])
    
    def send_email(self):
        """
        Отправка email-уведомления.
        Использует настройки из settings.py
        """
        if self.recipient.email:
            try:
                subject = 'Новое уведомление в системе ПТО'
                message = f"""
Здравствуйте, {self.recipient.get_full_name() or self.recipient.username}!

{self.text}

---
Это автоматическое уведомление из системы инженера ПТО.
Пожалуйста, не отвечайте на это письмо.
                """
                
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[self.recipient.email],
                    fail_silently=True,
                )
                return True
            except Exception as e:
                print(f"Ошибка отправки email: {e}")
                return False
        return False
    
    def save(self, *args, **kwargs):
        """При создании уведомления отправляем email"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # Отправляем email только для новых уведомлений
            self.send_email()
