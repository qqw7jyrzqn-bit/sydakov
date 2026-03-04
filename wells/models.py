"""
Модели приложения wells.
Управление скважинами и процессом согласования.
"""
from django.db import models
from django.conf import settings
from django.urls import reverse


class Well(models.Model):
    """
    Модель скважины.
    Проходит маршрут согласования через различные статусы.
    """
    
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('submitted', 'Отправлено на согласование'),
        ('approved_head', 'Согласовано НПТО'),
        ('rejected', 'Отклонено'),
        ('approved', 'Утверждено'),
        ('in_work', 'В работе'),
        ('drilling_completed', 'Бурение завершено'),
        ('archived', 'Архив'),
    ]
    
    name = models.CharField(
        max_length=200,
        verbose_name='Название скважины',
        help_text='Например: Скважина №123-А'
    )
    field = models.CharField(
        max_length=200,
        verbose_name='Месторождение'
    )
    coordinates = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Координаты',
        help_text='Географические координаты'
    )
    depth = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Глубина (м)',
        help_text='Проектная глубина в метрах'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Статус'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='wells_authored',
        verbose_name='Автор'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание',
        help_text='Дополнительная информация о скважине'
    )
    
    class Meta:
        verbose_name = 'Скважина'
        verbose_name_plural = 'Скважины'
        ordering = ['-created_at']
        permissions = [
            ('approve_well', 'Может согласовывать скважины'),
            ('generate_report', 'Может генерировать отчёты'),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"
    
    def get_absolute_url(self):
        return reverse('wells:well_detail', kwargs={'pk': self.pk})
    
    def send_for_approval(self, user):
        """Отправить скважину на согласование"""
        if self.status in ['draft', 'rejected']:
            self.status = 'submitted'
            self.save()
            # Сигнал создаст уведомление
            return True
        return False
    
    def approve_by_head(self, user, comment=''):
        """Согласование начальником ПТО"""
        if self.status == 'submitted' and user.is_head_pto():
            self.status = 'approved_head'
            self.save()
            
            # Создаём запись о согласовании
            ApprovalStep.objects.create(
                well=self,
                user=user,
                status='approved',
                comment=comment
            )
            return True
        return False
    
    def approve_final(self, user):
        """Окончательное утверждение"""
        if self.status == 'approved_head':
            self.status = 'approved'
            self.save()
            return True
        return False
    
    def reject(self, user, reason=''):
        """Отклонение скважины"""
        if self.status == 'submitted' and user.is_head_pto():
            self.status = 'rejected'
            self.save()
            
            # Создаём запись об отклонении
            ApprovalStep.objects.create(
                well=self,
                user=user,
                status='rejected',
                comment=reason
            )
            return True
        return False
    
    def start_work(self, user):
        """Начать работы по скважине"""
        if self.status == 'approved':
            self.status = 'in_work'
            self.save()
            return True
        return False
    
    def finish_drilling(self, user):
        """Завершить бурение"""
        if self.status == 'in_work':
            self.status = 'drilling_completed'
            self.save()
            return True
        return False
    
    def archive(self, user):
        """Отправить в архив"""
        if self.status == 'drilling_completed':
            self.status = 'archived'
            self.save()
            return True
        return False
    
    def can_edit(self, user):
        """Проверка, может ли пользователь редактировать скважину"""
        if user.is_head_pto():
            return True
        if user.is_pto_engineer() and self.status == 'draft':
            return True
        return False
    
    def get_status_badge_class(self):
        """Получить CSS-класс для бейджа статуса"""
        status_classes = {
            'draft': 'secondary',
            'submitted': 'info',
            'approved_head': 'primary',
            'approved': 'success',
            'in_work': 'warning',
            'drilling_completed': 'success',
            'archived': 'dark',
        }
        return status_classes.get(self.status, 'secondary')


class ApprovalStep(models.Model):
    """
    Модель шага согласования скважины.
    Хранит историю согласований различными пользователями.
    """
    
    STATUS_CHOICES = [
        ('approved', 'Согласовано'),
        ('rejected', 'Отклонено'),
        ('pending', 'Ожидает рассмотрения'),
    ]
    
    well = models.ForeignKey(
        Well,
        on_delete=models.CASCADE,
        related_name='approval_steps',
        verbose_name='Скважина'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name='Пользователь'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )
    comment = models.TextField(
        blank=True,
        verbose_name='Комментарий'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время'
    )
    
    class Meta:
        verbose_name = 'Шаг согласования'
        verbose_name_plural = 'Шаги согласования'
        ordering = ['timestamp']
        unique_together = [['well', 'user', 'timestamp']]
    
    def __str__(self):
        return f"{self.well.name} - {self.user.get_full_name()} ({self.get_status_display()})"
