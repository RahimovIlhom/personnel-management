import json

from django import forms
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import Personnel, PersonnelStatusHistory, Employee, Candidate
from .forms import EmployeeForm, CandidateForm
from apps.core.models import LanguageProficiency, StateAward, WorkExperience


class LanguageProficiencyInline(admin.TabularInline):
    model = LanguageProficiency
    extra = 1


class StateAwardInline(admin.TabularInline):
    model = StateAward
    extra = 1


class WorkExperienceInline(admin.TabularInline):
    model = WorkExperience
    extra = 1


class PersonnelStatusHistoryInline(admin.TabularInline):
    model = PersonnelStatusHistory
    readonly_fields = ('changed_by', 'old_status', 'new_status', 'created_at')
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class BasePersonnelAdmin(admin.ModelAdmin):
    """Asosiy PersonnelAdmin klassi"""
    inlines = [
        LanguageProficiencyInline,
        StateAwardInline,
        WorkExperienceInline,
        PersonnelStatusHistoryInline
    ]

    fieldsets = (
        (_('Asosiy ma’lumotlar'), {
            'fields': (
                'status', 'position', 'fullname'
            )
        }),
        (_('Shaxsiy hujjatlar'), {
            'fields': ('birthdate', 'birthplace', 'nationality', 'gender', 'pinfl', 'passport', 'resume')
        }),
        (_('Aloqa ma’lumotlari'), {
            'fields': (
                'place_of_residence', 'address_of_residence',
                'phone_number', 'additional_phone'
            )
        }),
        (_('Ta’lim ma’lumotlari'), {
            'fields': (
                'education_level',
                ('bachelor_university', 'bachelor_graduation_year'),
                ('master_university', 'master_graduation_year'),
            )
        }),
        (_('Ilmiy ma’lumotlar'), {
            'fields': (
                'academic_degree', 'academic_specialization',
                'academic_title', 'academic_title_date'
            ),
            'classes': ('collapse',)
        }),
    )

    list_filter = (
        'status',
        'position__department',
        'gender',
        'education_level',
        'nationality',
    )
    search_fields = (
        'fullname',
        'pinfl',
        'passport',
        'phone_number',
        'additional_phone',
        'bachelor_university',
        'master_university',
    )
    date_hierarchy = 'created_at'
    save_on_top = False

    def position_with_link(self, obj):
        url = reverse('admin:departments_position_change', args=[obj.position.id])
        return format_html('<a href="{}">{}</a>', url, obj.position)

    position_with_link.short_description = _('Lavozimi')

    def get_education(self, obj):
        education = []
        if obj.bachelor_university:
            education.append(f"{_('Bakalavr')}: {obj.bachelor_university}")
        if obj.master_university:
            education.append(f"{_('Magistr')}: {obj.master_university}")
        return " | ".join(education) if education else "-"

    get_education.short_description = _('Ta’lim')

    def save_model(self, request, obj, form, change):
        if change:
            old_obj = self.model.objects.get(pk=obj.pk)
            if old_obj.status != obj.status and obj.status == 'left':
                # Faqat xodim ishdan ketganda sabab so'rash
                reason = request.POST.get('status_change_reason')
                if not reason:
                    messages.error(request, _("Xodim ishdan ketganda sababini ko'rsating!"))
                    return
                obj.save(
                    changed_by=request.user,
                    status_change_reason=reason
                )
            else:
                # Boshqa holatlarda oddiy saqlash
                obj.save(changed_by=request.user)
        else:
            obj.save(changed_by=request.user)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Status tanlovlarini to'g'ridan-to'g'ri berish
        if isinstance(self, EmployeeAdmin):
            form.base_fields['status'].choices = Personnel.EMPLOYEE_STATUS_CHOICES
            # Agar xodim va status "left" bo'lsa, sabab maydonini ko'rsatish
            if obj and obj.status == 'left':
                form.base_fields['status_change_reason'] = forms.CharField(
                    label=_("Ishdan ketish sababi"),
                    widget=forms.Textarea,
                    required=True
                )
        else:
            form.base_fields['status'].choices = Personnel.CANDIDATE_STATUS_CHOICES
        return form

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        obj = self.get_object(request, object_id)
        if obj and obj.status == 'left':
            extra_context['show_reason_field'] = True
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context
        )


@admin.register(Employee)
class EmployeeAdmin(BasePersonnelAdmin):
    """Xodimlar uchun admin"""
    form = EmployeeForm
    list_display = ('fullname', 'status', 'position_with_link', 'phone_number', 'get_education')

    fieldsets = BasePersonnelAdmin.fieldsets + (
        (_('Ishlash davri'), {
            'fields': ('hired_date', 'left_date')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).filter(type='EMPLOYEE')


@admin.register(Candidate)
class CandidateAdmin(BasePersonnelAdmin):
    """Nomzodlar uchun admin"""
    form = CandidateForm
    list_display = ('fullname', 'status', 'position_with_link', 'phone_number', 'get_education')

    def get_queryset(self, request):
        return super().get_queryset(request).filter(type='CANDIDATE')

    actions = ['convert_to_employee']

    def convert_to_employee(self, request, queryset):
        """Tanlangan nomzodlarni xodimga o'tkazish"""
        success_count = 0
        error_count = 0

        for candidate in queryset:
            try:
                candidate.convert_to_employee()
                success_count += 1
            except ValidationError as e:
                messages.error(request, f"{candidate}: {e}")
                error_count += 1

        if success_count:
            messages.success(
                request,
                _("%(count)d ta nomzod muvaffaqiyatli xodimga o'tkazildi.") % {
                    'count': success_count
                }
            )
        if error_count:
            messages.warning(
                request,
                _("%(count)d ta nomzodni o'tkazib bo'lmadi.") % {
                    'count': error_count
                }
            )

    convert_to_employee.short_description = _("Tanlangan nomzodlarni xodimga o'tkazish")


@admin.register(PersonnelStatusHistory)
class PersonnelStatusHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'personnel',
        'old_status',
        'new_status',
        'changed_by',
        'created_at'
    )
    list_filter = (
        'personnel',
        'old_status',
        'new_status',
        'changed_by',
        'created_at'
    )
    search_fields = (
        'personnel__fullname',
        'reason',
        'changed_by__username'
    )
    readonly_fields = (
        'personnel',
        'old_status',
        'new_status',
        'changed_by',
        'created_at'
    )
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Personnel)
class PersonnelAdmin(BasePersonnelAdmin):
    """Personnel uchun yashirin admin"""
    def get_model_perms(self, request):
        """
        Bu model admin panelda ko'rinmasligi uchun
        """
        return {}
