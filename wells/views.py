"""
Views для приложения wells.
Управление скважинами, CRUD операции, согласование.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
import openpyxl
from openpyxl.styles import Font, Alignment

from .models import Well, ApprovalStep
from .forms import WellForm, ApprovalCommentForm, WellFilterForm, WellRejectForm
from accounts.mixins import (
    PTOEngineerRequiredMixin, 
    HeadPTORequiredMixin, 
    PTOStaffRequiredMixin,
    CanEditWellMixin,
    CanApproveWellMixin,
    pto_engineer_required,
    head_pto_required,
    pto_staff_required,
    can_edit_well_required,
)


def home(request):
    """
    Главная страница с информацией о системе.
    """
    from django.contrib.auth import get_user_model
    from documents.models import Document
    
    context = {}
    
    # Добавляем статистику для авторизованных пользователей
    if request.user.is_authenticated:
        context['total_wells'] = Well.objects.count()
        context['active_wells'] = Well.objects.filter(
            status__in=['in_work', 'submitted']
        ).count()
        context['total_documents'] = Document.objects.count()
        context['total_users'] = get_user_model().objects.count()
    
    return render(request, 'home.html', context)


@login_required
def dashboard(request):
    """
    Главная страница дашборда с таблицей скважин и фильтрами.
    """
    # Фильтруем скважины в зависимости от роли пользователя
    wells = request.user.get_accessible_wells()
    
    # Фильтрация по статусу
    status_filter = request.GET.get('status')
    if status_filter:
        wells = wells.filter(status=status_filter)
    
    # Поиск
    search = request.GET.get('search')
    if search:
        wells = wells.filter(
            Q(name__icontains=search) |
            Q(field__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Статистика для дашборда
    stats = {
        'total': Well.objects.count(),
        'draft': Well.objects.filter(status='draft').count(),
        'submitted': Well.objects.filter(status='submitted').count(),
        'rejected': Well.objects.filter(status='rejected').count(),
        'in_work': Well.objects.filter(status='in_work').count(),
        'completed': Well.objects.filter(status='drilling_completed').count(),
    }
    
    context = {
        'wells': wells,
        'stats': stats,
        'status_filter': status_filter,
        'search': search,
    }
    
    return render(request, 'wells/dashboard.html', context)


class WellListView(PTOStaffRequiredMixin, ListView):
    """Список всех скважин"""
    model = Well
    template_name = 'wells/well_list.html'
    context_object_name = 'wells'
    paginate_by = 20
    
    def get_queryset(self):
        """Фильтруем скважины по правам доступа"""
        return self.request.user.get_accessible_wells()


class WellDetailView(PTOStaffRequiredMixin, DetailView):
    """Детальная страница скважины с timeline согласований"""
    model = Well
    template_name = 'wells/well_detail.html'
    context_object_name = 'well'
    
    def get_queryset(self):
        """Проверка доступа к скважине"""
        return self.request.user.get_accessible_wells()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['approval_steps'] = self.object.approval_steps.all()
        context['comment_form'] = ApprovalCommentForm()
        # Передаем права пользователя в шаблон
        context['can_edit'] = self.request.user.can_edit_wells()
        context['can_approve'] = self.request.user.can_approve_wells()
        context['can_generate_docs'] = self.request.user.can_generate_documents()
        context['can_comment'] = self.request.user.can_comment_on_wells()
        context['can_send_for_approval'] = self.request.user.can_send_for_approval()
        return context


class WellCreateView(PTOStaffRequiredMixin, CreateView):
    model        = Well
    form_class   = WellForm
    template_name = 'wells/well_form.html'
    success_url   = reverse_lazy('wells:well_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Скважина успешно создана!')
        return super().form_valid(form)

class WellUpdateView(PTOStaffRequiredMixin, UpdateView):
    model        = Well
    form_class   = WellForm
    template_name = 'wells/well_form.html'

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_head_pto():
            qs = qs.filter(status__in=['draft', 'rejected'], author=self.request.user)
        return qs

    def form_valid(self, form):
        messages.success(self.request, 'Скважина успешно обновлена!')
        return super().form_valid(form)


class WellDeleteView(PTOStaffRequiredMixin, DeleteView):
    """Удаление скважины"""
    model = Well
    template_name = 'wells/well_confirm_delete.html'
    success_url = reverse_lazy('wells:well_list')
    
    def get_queryset(self):
        """Удалять можно только черновики"""
        qs = super().get_queryset()
        return qs.filter(status='draft')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Скважина успешно удалена!')
        return super().delete(request, *args, **kwargs)


@login_required
@pto_engineer_required
def well_send_for_approval(request, pk):
    """Отправить скважину на согласование"""
    well = get_object_or_404(Well, pk=pk)
    
    # Проверяем, что пользователь - автор скважины
    if well.author != request.user:
        messages.error(request, 'Вы можете отправлять на согласование только свои скважины.')
        return redirect('wells:well_detail', pk=pk)
    
    if well.send_for_approval(request.user):
        messages.success(request, f'Скважина "{well.name}" отправлена на согласование.')
    else:
        messages.error(request, 'Невозможно отправить скважину на согласование.')
    
    return redirect('wells:well_detail', pk=pk)


@login_required
@head_pto_required
def well_approve(request, pk):
    """Согласование скважины начальником ПТО"""
    well = get_object_or_404(Well, pk=pk)
    
    if request.method == 'POST':
        form = ApprovalCommentForm(request.POST)
        if form.is_valid():
            comment = form.cleaned_data.get('comment', '')
            if well.approve_by_head(request.user, comment):
                messages.success(request, f'Скважина "{well.name}" успешно согласована.')
            else:
                messages.error(request, 'Невозможно согласовать скважину.')
    
    return redirect('wells:well_detail', pk=pk)


@login_required
@head_pto_required
def well_reject(request, pk):
    """Отклонение скважины начальником ПТО"""
    well = get_object_or_404(Well, pk=pk)
    
    if request.method == 'POST':
        form = WellRejectForm(request.POST)
        if form.is_valid():
            reason = form.cleaned_data['reason']
            if well.reject(request.user, reason):
                messages.warning(request, f'Скважина "{well.name}" отклонена.')
            else:
                messages.error(request, 'Невозможно отклонить скважину.')
            return redirect('wells:well_detail', pk=pk)
    else:
        form = WellRejectForm()
    
    # Если GET запрос - показываем форму в контексте detail страницы
    return redirect('wells:well_detail', pk=pk)


@login_required
@head_pto_required
def well_change_status(request, pk):
    """Изменение статуса скважины (только для начальника ПТО)"""
    well = get_object_or_404(Well, pk=pk)
    
    new_status = request.POST.get('new_status')
    
    if new_status == 'approved' and well.status == 'approved_head':
        well.approve_final(request.user)
        messages.success(request, 'Скважина окончательно утверждена.')
    elif new_status == 'in_work' and well.status == 'approved':
        well.start_work(request.user)
        messages.success(request, 'Работы по скважине начаты.')
    elif new_status == 'drilling_completed' and well.status == 'in_work':
        well.finish_drilling(request.user)
        messages.success(request, 'Бурение завершено.')
    elif new_status == 'archived' and well.status == 'drilling_completed':
        well.archive(request.user)
        messages.success(request, 'Скважина отправлена в архив.')
    else:
        messages.error(request, 'Недопустимое изменение статуса.')
    
    return redirect('wells:well_detail', pk=pk)


@login_required
@pto_staff_required
def export_wells_excel(request):
    """Экспорт списка скважин в Excel"""
    # Создание workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Скважины"
    
    # Заголовки
    headers = ['№', 'Название', 'Месторождение', 'Глубина (м)', 'Статус', 'Автор', 'Дата создания']
    ws.append(headers)
    
    # Стилизация заголовков
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')
    
    # Данные - только доступные пользователю скважины
    wells = request.user.get_accessible_wells()
    for idx, well in enumerate(wells, start=1):
        ws.append([
            idx,
            well.name,
            well.field,
            float(well.depth),
            well.get_status_display(),
            well.author.get_full_name() or well.author.username,
            well.created_at.strftime('%d.%m.%Y %H:%M')
        ])
    
    # Автоширина колонок
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    # Создание HTTP ответа
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=wells_export.xlsx'
    
    wb.save(response)
    return response


@login_required
def advanced_search(request):
    """Расширенный поиск скважин"""
    from .forms_extended import AdvancedSearchForm
    
    form = AdvancedSearchForm(request.GET or None)
    wells = request.user.get_accessible_wells()
    
    if form.is_valid():
        # Поиск по тексту
        if form.cleaned_data.get('query'):
            query = form.cleaned_data['query']
            wells = wells.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(field__icontains=query)
            )
        
        # Фильтр по месторождению
        if form.cleaned_data.get('field'):
            wells = wells.filter(field__icontains=form.cleaned_data['field'])
        
        # Фильтр по статусу
        if form.cleaned_data.get('status'):
            wells = wells.filter(status=form.cleaned_data['status'])
        
        # Фильтр по автору
        if form.cleaned_data.get('author'):
            author = form.cleaned_data['author']
            wells = wells.filter(
                Q(author__username__icontains=author) |
                Q(author__first_name__icontains=author) |
                Q(author__last_name__icontains=author)
            )
        
        # Фильтр по глубине
        if form.cleaned_data.get('depth_min'):
            wells = wells.filter(depth__gte=form.cleaned_data['depth_min'])
        if form.cleaned_data.get('depth_max'):
            wells = wells.filter(depth__lte=form.cleaned_data['depth_max'])
        
        # Фильтр по дате создания
        if form.cleaned_data.get('created_from'):
            wells = wells.filter(created_at__date__gte=form.cleaned_data['created_from'])
        if form.cleaned_data.get('created_to'):
            wells = wells.filter(created_at__date__lte=form.cleaned_data['created_to'])
    
    context = {
        'form': form,
        'wells': wells,
        'total_found': wells.count(),
    }
    
    return render(request, 'wells/advanced_search.html', context)
