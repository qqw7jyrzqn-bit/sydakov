"""
Forms для приложения wells.
"""
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from .models import Well, ApprovalStep


class WellForm(forms.ModelForm):
    """Форма для создания и редактирования скважины"""
    
    class Meta:
        model = Well
        fields = ['name', 'field', 'coordinates', 'depth', 'description', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-6 mb-3'),
                Column('field', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('coordinates', css_class='form-group col-md-6 mb-3'),
                Column('depth', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('status', css_class='form-group col-md-6 mb-3'),
            ),
            'description',
            Submit('submit', 'Сохранить', css_class='btn btn-primary')
        )


class ApprovalCommentForm(forms.Form):
    """Форма для комментария при согласовании"""
    
    comment = forms.CharField(
        label='Комментарий',
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False
    )


class WellRejectForm(forms.Form):
    """Форма для отказа в согласовании"""
    reason = forms.CharField(
        label='Причина отказа',
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Укажите причину отказа в согласовании', 'class': 'form-control'}),
        required=True,
        help_text='Обязательно укажите причину отказа'
    )


class WellFilterForm(forms.Form):
    """Форма фильтрации скважин на дашборде"""
    status = forms.ChoiceField(
        choices=[('', 'Все статусы')] + Well.STATUS_CHOICES,
        required=False,
        label='Статус'
    )

