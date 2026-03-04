"""
Views для приложения accounts.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def profile(request):
    """Страница профиля пользователя"""
    return render(request, 'accounts/profile.html', {
        'user': request.user,
    })
