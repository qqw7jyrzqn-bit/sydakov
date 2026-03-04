"""
URL configuration for pto_info_system project.
Маршрутизация для системы инженера ПТО.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Аутентификация
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Приложения
    path('', include('wells.urls')),
    path('accounts/', include('accounts.urls')),
    path('documents/', include('documents.urls')),
    path('notifications/', include('notifications.urls')),

    path('analytics/', include('analytics.urls')),
]

# Медиа файлы
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # В режиме DEBUG Django автоматически обслуживает статику из STATICFILES_DIRS

# Настройка заголовков админки
admin.site.site_header = "Система инженера ПТО"
admin.site.site_title = "ПТО Администрирование"
admin.site.index_title = "Управление системой"
