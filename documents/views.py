"""
Views для приложения documents.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from django.http import FileResponse, Http404

from .models import Document
from .forms import DocumentForm
from wells.models import Well
from accounts.mixins import PTOStaffRequiredMixin, can_generate_documents_required


class DocumentListView(LoginRequiredMixin, ListView):
    """Список документов"""
    model = Document
    template_name = 'documents/document_list.html'
    context_object_name = 'documents'
    paginate_by = 20
    
    def get_queryset(self):
        qs = super().get_queryset()
        # Фильтруем документы по доступным пользователю скважинам
        accessible_wells = self.request.user.get_accessible_wells()
        qs = qs.filter(well__in=accessible_wells)
        
        well_id = self.request.GET.get('well')
        if well_id:
            qs = qs.filter(well_id=well_id)
        return qs


class DocumentCreateView(PTOStaffRequiredMixin, CreateView):
    """Загрузка нового документа"""
    model = Document
    form_class = DocumentForm
    template_name = 'documents/document_form.html'
    success_url = reverse_lazy('documents:document_list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Ограничиваем выбор скважин доступными пользователю
        form.fields['well'].queryset = self.request.user.get_accessible_wells()
        return form
    
    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        messages.success(self.request, 'Документ успешно загружен!')
        return super().form_valid(form)


@login_required
def generate_report(request, well_id):
    """
    Генерация Word-отчёта по скважине.
    Создаёт документ и возвращает его для скачивания.
    Поставщики могут скачивать, но не генерировать новые документы.
    """
    # Проверяем доступ к скважине
    accessible_wells = request.user.get_accessible_wells()
    well = get_object_or_404(accessible_wells, pk=well_id)
    
    # Получаем тип документа из параметра запроса
    doc_type = request.GET.get('type', 'report')
    
    # Названия типов документов
    doc_type_names = {
        'report': 'Отчёт по скважине',
        'technical_spec': 'Техническое задание',
        'protocol': 'Протокол испытаний',
        'geology_report': 'Геологический отчёт',
        'drilling_program': 'Программа бурения',
        'completion_report': 'Акт завершения',
        'safety_plan': 'План по безопасности',
        'other': 'Документ'
    }
    
    # Ищем существующий документ данного типа
    document = Document.objects.filter(
        well=well,
        document_type=doc_type
    ).first()
    
    # Создаём новый документ, если его нет
    try:
        if not document:
            if not request.user.can_generate_documents():
                messages.error(request, 'У вас нет прав на генерацию документов.')
                return redirect('wells:well_detail', pk=well_id)
            
            document = Document.objects.create(
                well=well,
                title=f'{doc_type_names.get(doc_type, "Документ")} - {well.name}',
                document_type=doc_type,
                uploaded_by=request.user,
                description=f'Автоматически сгенерированный документ типа "{doc_type_names.get(doc_type)}"'
            )
    except Exception as e:
        messages.error(request, f'Ошибка при создании документа: {str(e)}')
        return redirect('wells:well_detail', pk=well_id)
    
    # Генерируем отчёт
    try:
        url = document.generate_docx()
        
        # Обновляем объект из БД, чтобы получить актуальное состояние файла
        document.refresh_from_db()
        
        # Проверяем, что файл действительно сохранен
        if not document.generated_docx:
            raise Exception('Файл не был сохранён в базе данных')
        
        messages.success(request, f'{doc_type_names.get(doc_type, "Документ")} успешно сгенерирован!')
        
        # Отдаём файл для скачивания
        return FileResponse(
            document.generated_docx.open('rb'),
            as_attachment=True,
            filename=document.generated_docx.name.split('/')[-1]
        )
    except Exception as e:
        messages.error(request, f'Ошибка при генерации документа: {str(e)}')
        return redirect('wells:well_detail', pk=well_id)


@login_required
def download_document(request, pk):
    """Скачивание документа"""
    document = get_object_or_404(Document, pk=pk)
    
    # Проверяем доступ пользователя к скважине документа
    accessible_wells = request.user.get_accessible_wells()
    if document.well not in accessible_wells:
        messages.error(request, 'У вас нет доступа к этому документу.')
        return redirect('documents:document_list')
    
    # Обновляем объект из БД на всякий случай
    document.refresh_from_db()
    
    # Проверяем наличие файла (загруженный или сгенерированный)
    file_to_download = document.file or document.generated_docx
    
    if file_to_download:
        try:
            # Проверяем существование файла на диске
            if not file_to_download.storage.exists(file_to_download.name):
                messages.error(request, f'Файл не найден на диске: {file_to_download.name}')
                return redirect('wells:well_detail', pk=document.well.pk)
            
            return FileResponse(
                file_to_download.open('rb'),
                as_attachment=True,
                filename=file_to_download.name.split('/')[-1]
            )
        except Exception as e:
            messages.error(request, f'Ошибка при скачивании файла: {str(e)}')
            return redirect('wells:well_detail', pk=document.well.pk)
    else:
        messages.error(request, 'У документа нет прикреплённого файла.')
        return redirect('wells:well_detail', pk=document.well.pk)
