"""
Миксины для проверки прав доступа пользователей.
"""
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


class PTOEngineerRequiredMixin(UserPassesTestMixin):
    """Миксин для проверки прав инженера ПТО"""
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_pto_engineer()
    
    def handle_no_permission(self):
        messages.error(self.request, 'У вас нет прав для выполнения этого действия. Требуется роль "Инженер ПТО".')
        return redirect('wells:home')


class HeadPTORequiredMixin(UserPassesTestMixin):
    """Миксин для проверки прав начальника ПТО"""
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_head_pto()
    
    def handle_no_permission(self):
        messages.error(self.request, 'Только начальник ПТО может выполнить это действие.')
        return redirect('wells:home')


class PTOStaffRequiredMixin(UserPassesTestMixin):
    """Миксин для проверки прав сотрудников ПТО (инженер + начальник)"""
    
    def test_func(self):
        return self.request.user.is_authenticated and \
               self.request.user.role in ['pto_engineer', 'head_pto']
    
    def handle_no_permission(self):
        messages.error(self.request, 'Доступ разрешен только сотрудникам ПТО.')
        return redirect('wells:home')


class CanEditWellMixin(UserPassesTestMixin):
    """Миксин для проверки прав на редактирование скважин"""
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.can_edit_wells()
    
    def handle_no_permission(self):
        messages.error(self.request, 'У вас нет прав на редактирование скважин.')
        return redirect('wells:home')


class CanApproveWellMixin(UserPassesTestMixin):
    """Миксин для проверки прав на согласование скважин"""
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.can_approve_wells()
    
    def handle_no_permission(self):
        messages.error(self.request, 'Только начальник ПТО может согласовывать скважины.')
        return redirect('wells:home')


# Декораторы для function-based views

def pto_engineer_required(view_func):
    """Декоратор для проверки роли инженера ПТО"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Необходима авторизация.')
            return redirect('login')
        if not request.user.is_pto_engineer():
            messages.error(request, 'Требуется роль "Инженер ПТО".')
            return redirect('wells:home')
        return view_func(request, *args, **kwargs)
    return wrapper


def head_pto_required(view_func):
    """Декоратор для проверки роли начальника ПТО"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Необходима авторизация.')
            return redirect('login')
        if not request.user.can_approve_wells():
            messages.error(request, 'Только начальник ПТО может выполнить это действие.')
            return redirect('wells:home')
        return view_func(request, *args, **kwargs)
    return wrapper


def pto_staff_required(view_func):
    """Декоратор для проверки прав сотрудников ПТО"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Необходима авторизация.')
            return redirect('login')
        if request.user.role not in ['pto_engineer', 'head_pto']:
            messages.error(request, 'Доступ разрешен только сотрудникам ПТО.')
            return redirect('wells:home')
        return view_func(request, *args, **kwargs)
    return wrapper


def can_edit_well_required(view_func):
    """Декоратор для проверки прав на редактирование скважин"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Необходима авторизация.')
            return redirect('login')
        if not request.user.can_edit_wells():
            messages.error(request, 'У вас нет прав на редактирование скважин.')
            return redirect('wells:home')
        return view_func(request, *args, **kwargs)
    return wrapper


def can_generate_documents_required(view_func):
    """Декоратор для проверки прав на генерацию документов"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Необходима авторизация.')
            return redirect('login')
        if not request.user.can_generate_documents():
            messages.error(request, 'У вас нет прав на генерацию документов.')
            return redirect('wells:home')
        return view_func(request, *args, **kwargs)
    return wrapper
