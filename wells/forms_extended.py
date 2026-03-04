"""
Формы для расширенных моделей.
"""
from django import forms
from .models_extended import Comment, Tag, WellDeadline, WellAttachment


class CommentForm(forms.ModelForm):
    """Форма добавления комментария"""
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ваш комментарий...'
            })
        }
        labels = {
            'text': ''
        }


class TagForm(forms.ModelForm):
    """Форма создания тега"""
    class Meta:
        model = Tag
        fields = ['name', 'color', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2
            })
        }


class WellDeadlineForm(forms.ModelForm):
    """Форма дедлайна"""
    class Meta:
        model = WellDeadline
        fields = ['milestone', 'planned_date', 'actual_date', 'responsible', 'notes']
        widgets = {
            'milestone': forms.Select(attrs={'class': 'form-select'}),
            'planned_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'actual_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'responsible': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2
            })
        }


class WellAttachmentForm(forms.ModelForm):
    """Форма загрузки вложения"""
    class Meta:
        model = WellAttachment
        fields = ['file', 'title', 'category', 'description']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2
            })
        }


class AdvancedSearchForm(forms.Form):
    """Расширенная форма поиска"""
    
    query = forms.CharField(
        required=False,
        label='Поиск по названию/описанию',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите текст для поиска...'
        })
    )
    
    field = forms.CharField(
        required=False,
        label='Месторождение',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Название месторождения'
        })
    )
    
    status = forms.ChoiceField(
        required=False,
        label='Статус',
        choices=[('', 'Все статусы')] + [
            ('draft', 'Черновик'),
            ('submitted', 'На согласовании'),
            ('approved', 'Согласовано'),
            ('rejected', 'Отклонено'),
            ('in_work', 'В работе'),
            ('completed', 'Завершено'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    author = forms.CharField(
        required=False,
        label='Автор',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Имя автора'
        })
    )
    
    depth_min = forms.DecimalField(
        required=False,
        label='Глубина от (м)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0'
        })
    )
    
    depth_max = forms.DecimalField(
        required=False,
        label='Глубина до (м)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '10000'
        })
    )
    
    created_from = forms.DateField(
        required=False,
        label='Создано с',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    created_to = forms.DateField(
        required=False,
        label='Создано по',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
