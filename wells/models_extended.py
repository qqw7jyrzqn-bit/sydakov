"""
Расширенные модели для wells приложения.
Комментарии, теги, история изменений.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone


class Comment(models.Model):
    """Комментарии к скважинам"""
    well = models.ForeignKey(
        'wells.Well',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Скважина'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    text = models.TextField(verbose_name='Текст комментария')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлён')
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name='Ответ на'
    )
    
    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Комментарий {self.author.username} к {self.well.name}"


class Tag(models.Model):
    """Теги для группировки скважин"""
    name = models.CharField(max_length=50, unique=True, verbose_name='Название')
    color = models.CharField(
        max_length=7,
        default='#0d6efd',
        verbose_name='Цвет',
        help_text='HEX цвет, например #0d6efd'
    )
    description = models.TextField(blank=True, verbose_name='Описание')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Создал'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    
    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class WellHistory(models.Model):
    """История изменений скважины"""
    
    ACTION_CHOICES = [
        ('created', 'Создана'),
        ('updated', 'Обновлена'),
        ('status_changed', 'Изменён статус'),
        ('submitted', 'Отправлена на согласование'),
        ('approved', 'Согласована'),
        ('rejected', 'Отклонена'),
        ('deleted', 'Удалена'),
    ]
    
    well = models.ForeignKey(
        'wells.Well',
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name='Скважина'
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name='Действие'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Пользователь'
    )
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Время')
    old_value = models.TextField(blank=True, verbose_name='Старое значение')
    new_value = models.TextField(blank=True, verbose_name='Новое значение')
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP адрес')
    
    class Meta:
        verbose_name = 'История изменений'
        verbose_name_plural = 'История изменений'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.well.name} - {self.get_action_display()} ({self.timestamp:%d.%m.%Y %H:%M})"


class WellDeadline(models.Model):
    """Дедлайны и вехи проекта скважины"""
    
    MILESTONE_CHOICES = [
        ('design', 'Проектирование'),
        ('approval', 'Согласование'),
        ('drilling_start', 'Начало бурения'),
        ('drilling_end', 'Окончание бурения'),
        ('testing', 'Испытания'),
        ('commissioning', 'Ввод в эксплуатацию'),
    ]
    
    well = models.ForeignKey(
        'wells.Well',
        on_delete=models.CASCADE,
        related_name='deadlines',
        verbose_name='Скважина'
    )
    milestone = models.CharField(
        max_length=20,
        choices=MILESTONE_CHOICES,
        verbose_name='Веха'
    )
    planned_date = models.DateField(verbose_name='Плановая дата')
    actual_date = models.DateField(null=True, blank=True, verbose_name='Фактическая дата')
    is_completed = models.BooleanField(default=False, verbose_name='Завершено')
    responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Ответственный'
    )
    notes = models.TextField(blank=True, verbose_name='Примечания')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    
    class Meta:
        verbose_name = 'Дедлайн'
        verbose_name_plural = 'Дедлайны'
        ordering = ['planned_date']
        unique_together = [['well', 'milestone']]
    
    def __str__(self):
        return f"{self.well.name} - {self.get_milestone_display()}"
    
    @property
    def is_overdue(self):
        """Проверка просрочки"""
        if self.is_completed:
            return False
        return timezone.now().date() > self.planned_date
    
    @property
    def days_remaining(self):
        """Дней до дедлайна"""
        if self.is_completed:
            return 0
        delta = self.planned_date - timezone.now().date()
        return delta.days


class WellAttachment(models.Model):
    """Дополнительные файлы к скважине"""
    
    CATEGORY_CHOICES = [
        ('photo', 'Фотография'),
        ('drawing', 'Чертёж'),
        ('report', 'Отчёт'),
        ('certificate', 'Сертификат'),
        ('other', 'Другое'),
    ]
    
    well = models.ForeignKey(
        'wells.Well',
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name='Скважина'
    )
    file = models.FileField(
        upload_to='well_attachments/%Y/%m/',
        verbose_name='Файл'
    )
    title = models.CharField(max_length=200, verbose_name='Название')
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='other',
        verbose_name='Категория'
    )
    description = models.TextField(blank=True, verbose_name='Описание')
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Загрузил'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Загружен')
    file_size = models.IntegerField(null=True, blank=True, verbose_name='Размер (байт)')
    
    class Meta:
        verbose_name = 'Вложение'
        verbose_name_plural = 'Вложения'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.title} - {self.well.name}"
    
    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)
    
    @property
    def file_size_mb(self):
        """Размер в МБ"""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return 0
