from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Sum
from .models import DepartmentType, Department, Position

@admin.register(DepartmentType)
class DepartmentTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_departments_count')
    search_fields = ('name',)
    ordering = ('name',)

    def get_departments_count(self, obj):
        return obj.departments.count()
    get_departments_count.short_description = _("Bo‘limlar soni")

class PositionInline(admin.TabularInline):
    model = Position
    extra = 1
    fields = ('name', 'number_of_jobs')
    verbose_name = _("Lavozim")
    verbose_name_plural = _("Lavozimlar")

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'get_positions_count', 'get_total_jobs')
    list_filter = ('type',)
    search_fields = ('name', 'type__name')
    ordering = ('type', 'name')
    inlines = [PositionInline]
    autocomplete_fields = ['type']

    def get_positions_count(self, obj):
        return obj.positions.count()
    get_positions_count.short_description = _("Lavozimlar soni")

    def get_total_jobs(self, obj):
        return obj.positions.aggregate(total=Sum('number_of_jobs'))['total'] or 0
    get_total_jobs.short_description = _("Jami shtat birliklari")

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'number_of_jobs', 'get_employees_count')
    list_filter = ('department', 'department__type')
    search_fields = ('name', 'department__name')
    ordering = ('department', 'name')
    autocomplete_fields = ['department']

    fieldsets = (
        (_('Asosiy ma’lumotlar'), {
            'fields': ('name', 'department')
        }),
        (_('Shtat ma’lumotlari'), {
            'fields': ('number_of_jobs',),
            'description': _('Ushbu lavozimdagi mavjud shtat birliklari sonini kiriting')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'department', 
            'department__type'
        ).annotate(
            employees_count=Count('personnel')
        )

    def get_employees_count(self, obj):
        count = getattr(obj, 'employees_count', 0)
        if count > obj.number_of_jobs:
            return f"{count} / {obj.number_of_jobs} ⚠️"
        return f"{count} / {obj.number_of_jobs}"
    get_employees_count.short_description = _("Band/Jami")

    class Media:
        css = {
            'all': ('admin/css/position.css',)
        }
