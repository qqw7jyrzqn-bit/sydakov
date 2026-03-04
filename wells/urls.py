"""
URL-маршруты для приложения wells.
"""
from django.urls import path
from . import views

app_name = 'wells'

urlpatterns = [
    # Главная страница
    path('', views.home, name='home'),
    
    # CRUD для скважин
    path('wells/', views.WellListView.as_view(), name='well_list'),
    path('wells/<int:pk>/', views.WellDetailView.as_view(), name='well_detail'),
    path('wells/create/', views.WellCreateView.as_view(), name='well_create'),
    path('wells/<int:pk>/edit/', views.WellUpdateView.as_view(), name='well_update'),
    path('wells/<int:pk>/delete/', views.WellDeleteView.as_view(), name='well_delete'),
    
    # Действия со скважинами
    path('wells/<int:pk>/send-approval/', views.well_send_for_approval, name='well_send_approval'),
    path('wells/<int:pk>/approve/', views.well_approve, name='well_approve'),
    path('wells/<int:pk>/reject/', views.well_reject, name='well_reject'),
    path('wells/<int:pk>/change-status/', views.well_change_status, name='well_change_status'),
    
    # Экспорт
    path('wells/export/excel/', views.export_wells_excel, name='export_wells_excel'),
    
    # Расширенный поиск
    path('search/', views.advanced_search, name='advanced_search'),
]
