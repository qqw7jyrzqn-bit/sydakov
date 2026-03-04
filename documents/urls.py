"""
URL-маршруты для приложения documents.
"""
from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('', views.DocumentListView.as_view(), name='document_list'),
    path('create/', views.DocumentCreateView.as_view(), name='document_create'),
    path('<int:pk>/download/', views.download_document, name='document_download'),
    path('generate-report/<int:well_id>/', views.generate_report, name='generate_report'),
]
