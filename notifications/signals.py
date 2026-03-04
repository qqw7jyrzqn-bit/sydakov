"""
Signals для отправки email-уведомлений.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import Notification


@receiver(post_save, sender=Notification)
def send_notification_email(sender, instance, created, **kwargs):
    """
    Отправляет email при создании нового уведомления.
    """
    if created and instance.recipient.email:
        try:
            # Тема письма
            subject = f'[Система ПТО] Новое уведомление'
            
            # Текст письма
            message = f"""
Здравствуйте, {instance.recipient.get_full_name() or instance.recipient.username}!

У вас новое уведомление в системе ПТО:

{instance.text}

---
Дата: {instance.created_at.strftime('%d.%m.%Y %H:%M')}

Перейдите в систему для просмотра деталей: {settings.SITE_URL}

С уважением,
Система управления ПТО
            """
            
            # HTML версия (опционально)
            html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f8f9fa; padding: 20px; }}
        .notification {{ background: white; padding: 15px; border-left: 4px solid #667eea; 
                        margin: 15px 0; border-radius: 4px; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
        .btn {{ display: inline-block; padding: 10px 20px; background: #667eea; 
                color: white; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>🔔 Новое уведомление</h2>
        </div>
        <div class="content">
            <p>Здравствуйте, <strong>{instance.recipient.get_full_name() or instance.recipient.username}</strong>!</p>
            
            <div class="notification">
                <p>{instance.text}</p>
                <small style="color: #666;">
                    📅 {instance.created_at.strftime('%d.%m.%Y %H:%M')}
                </small>
            </div>
            
            <a href="{settings.SITE_URL}" class="btn">Перейти в систему</a>
        </div>
        <div class="footer">
            Это автоматическое сообщение от системы управления ПТО.<br>
            Не отвечайте на это письмо.
        </div>
    </div>
</body>
</html>
            """
            
            # Отправка email
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.recipient.email],
                html_message=html_message,
                fail_silently=True,  # Не падать при ошибке отправки
            )
            
            print(f'✉️ Email отправлен: {instance.recipient.email} - {subject}')
            
        except Exception as e:
            print(f'❌ Ошибка отправки email: {e}')
