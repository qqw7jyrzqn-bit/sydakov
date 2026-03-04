"""
URL-маршруты для приложения supplier_portal.
"""
from django.urls import path
from . import views

app_name = 'supplier_portal'

urlpatterns = [
    path('', views.supplier_dashboard, name='dashboard'),
    path('document/<int:pk>/', views.supplier_document_detail, name='document_detail'),
    path('upload-report/<int:document_id>/', views.supplier_upload_report, name='upload_report'),
]
