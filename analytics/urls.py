"""
URL конфигурация для analytics.
"""
from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.analytics_dashboard, name='dashboard'),
    path('field/<str:field_name>/', views.field_report, name='field_report'),
    path('performance/', views.performance_report, name='performance_report'),
]
