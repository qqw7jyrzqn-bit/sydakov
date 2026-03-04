"""
Forms для приложения documents.
"""
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from .models import Document


class DocumentForm(forms.ModelForm):
    """Форма для загрузки документа"""
    
    class Meta:
        model = Document
        fields = ['well', 'title', 'document_type', 'file', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'well',
            'title',
            'document_type',
            'file',
            'description',
            Submit('submit', 'Загрузить', css_class='btn btn-primary')
        )
