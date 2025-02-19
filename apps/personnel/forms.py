from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Personnel


class BasePersonnelForm(forms.ModelForm):
    """Asosiy Personnel form"""
    status = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
        choices=[],  # Bo'sh choices, keyinroq to'ldiriladi
        label=_('Holati')
    )

    class Meta:
        model = Personnel
        fields = '__all__'
        exclude = ['type']


class EmployeeForm(BasePersonnelForm):
    """Xodimlar uchun form"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.type = 'EMPLOYEE'
        self.fields['status'].choices = Personnel.EMPLOYEE_STATUS_CHOICES
        self.fields['status'].initial = 'working'


class CandidateForm(BasePersonnelForm):
    """Nomzodlar uchun form"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.type = 'CANDIDATE'
        self.fields['status'].choices = Personnel.CANDIDATE_STATUS_CHOICES
        self.fields['status'].initial = 'submitted'