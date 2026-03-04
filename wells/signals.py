"""
Сигналы для приложения wells.
Обработка изменений статусов скважин и создание уведомлений.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Well, ApprovalStep


@receiver(pre_save, sender=Well)
def well_status_changed(sender, instance, **kwargs):
    """
    Обработка изменения статуса скважины.
    Создаёт уведомления для заинтересованных пользователей.
    """
    if instance.pk:
        try:
            old_instance = Well.objects.get(pk=instance.pk)
            if old_instance.status != instance.status:
                # Статус изменился - создадим уведомление
                # Это будет обработано в приложении notifications
                instance._status_changed = True
                instance._old_status = old_instance.status
        except Well.DoesNotExist:
            pass


@receiver(post_save, sender=Well)
def create_status_notification(sender, instance, created, **kwargs):
    """Создание уведомления после изменения статуса"""
    if hasattr(instance, '_status_changed') and instance._status_changed:
        # Импортируем здесь, чтобы избежать циклических импортов
        from notifications.models import Notification
        from accounts.models import User
        
        # Определяем, кого уведомить
        recipients = []
        
        if instance.status == 'submitted':
            # Уведомить всех начальников ПТО
            recipients = User.objects.filter(role='head_pto')
        elif instance.status in ['approved_head', 'approved']:
            # Уведомить автора
            recipients = [instance.author]
        elif instance.status == 'rejected':
            # Уведомить автора об отклонении
            recipients = [instance.author]
        elif instance.status == 'in_work':
            # Уведомить автора и начальника
            recipients = [instance.author] + list(User.objects.filter(role='head_pto'))
        
        # Создаём уведомления
        for recipient in recipients:
            Notification.objects.create(
                recipient=recipient,
                text=f'Скважина "{instance.name}" изменила статус на "{instance.get_status_display()}"',
                well=instance
            )


@receiver(post_save, sender=ApprovalStep)
def approval_step_notification(sender, instance, created, **kwargs):
    """Уведомление при добавлении комментария к согласованию"""
    if created and instance.comment:
        from notifications.models import Notification
        
        # Уведомить автора скважины
        Notification.objects.create(
            recipient=instance.well.author,
            text=f'{instance.user.get_full_name()} оставил комментарий к скважине "{instance.well.name}"',
            well=instance.well
        )
