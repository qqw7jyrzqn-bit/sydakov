"""
Модели приложения accounts.
Кастомная модель пользователя с ролями для системы ПТО.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q


class User(AbstractUser):
    """
    Расширенная модель пользователя с ролями и дополнительными полями.
    
    Роли:
    - pto_engineer: Инженер ПТО (полный CRUD)
    - head_pto: Начальник ПТО (согласование/утверждение)
    """
    
    ROLE_CHOICES = [
        ('pto_engineer', 'Инженер ПТО'),
        ('head_pto', 'Начальник ПТО'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='pto_engineer',
        verbose_name='Роль'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Телефон'
    )
    company = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Компания'
    )
    signature = models.ImageField(
        upload_to='signatures/',
        blank=True,
        null=True,
        verbose_name='Подпись'
    )
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
    
    def is_pto_engineer(self):
        """Проверка, является ли пользователь инженером ПТО"""
        return self.role == 'pto_engineer'
    
    def is_head_pto(self):
        """Проверка, является ли пользователь начальником ПТО"""
        return self.role == 'head_pto'
    
    def can_edit_wells(self):
        """Может ли пользователь редактировать скважины"""
        return self.role in ['pto_engineer', 'head_pto']
    
    def can_approve_wells(self):
        """Может ли пользователь согласовывать скважины"""
        return self.role == 'head_pto'
    
    def can_create_wells(self):
        """Может ли пользователь создавать скважины"""
        return self.role in ['pto_engineer', 'head_pto']
    
    def can_delete_wells(self):
        """Может ли пользователь удалять скважины"""
        return self.role in ['pto_engineer', 'head_pto']
    
    def can_generate_documents(self):
        """Может ли пользователь генерировать документы"""
        return self.role in ['pto_engineer', 'head_pto']
    
    def can_upload_documents(self):
        """Может ли пользователь загружать документы"""
        return self.role in ['pto_engineer', 'head_pto']
    
    def can_view_all_wells(self):
        """Может ли пользователь видеть все скважины"""
        return self.role == 'head_pto'
    
    def can_comment_on_wells(self):
        """Может ли пользователь комментировать скважины"""
        return self.role in ['pto_engineer', 'head_pto']
    
    def can_send_for_approval(self):
        """Может ли пользователь отправлять на согласование"""
        return self.role == 'pto_engineer'
    
    def can_reject_wells(self):
        """Может ли пользователь отклонять скважины"""
        return self.role == 'head_pto'
    
    def can_change_well_status(self):
        """Может ли пользователь изменять статусы скважин"""
        return self.role == 'head_pto'
    
    def can_access_analytics(self):
        """Может ли пользователь видеть аналитику"""
        return self.role == 'head_pto'
    
    def get_accessible_wells(self):
        """Возвращает QuerySet скважин, доступных пользователю"""
        from wells.models import Well
        
        if self.role == 'head_pto':
            # Начальник ПТО видит все скважины
            return Well.objects.all()
        elif self.role == 'pto_engineer':
            # Инженер видит только свои скважины
            return Well.objects.filter(author=self)
        else:
            return Well.objects.none()
