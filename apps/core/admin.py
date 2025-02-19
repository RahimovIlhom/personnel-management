from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    Region, District, Nation, EducationLevel,
    AcademicDegree, AcademicSpecialization, AcademicTitle,
    LanguageProficiency, StateAward, WorkExperience
)
from ..personnel.models import Employee, Candidate


class DistrictInline(admin.TabularInline):
    model = District
    extra = 1

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_districts_count')
    search_fields = ('name',)
    ordering = ('name',)
    inlines = [DistrictInline]

    def get_districts_count(self, obj):
        return obj.districts.count()
    get_districts_count.short_description = _("Tumanlar soni")

@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'region')
    list_filter = ('region',)
    search_fields = ('name', 'region__name')
    ordering = ('region', 'name')
    autocomplete_fields = ['region']

@admin.register(Nation)
class NationAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(EducationLevel)
class EducationLevelAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(AcademicDegree)
class AcademicDegreeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(AcademicSpecialization)
class AcademicSpecializationAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(AcademicTitle)
class AcademicTitleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(LanguageProficiency)
class LanguageProficiencyAdmin(admin.ModelAdmin):
    list_display = ('personnel', 'get_language_display', 'get_level_display', )
    list_filter = ('language_name', 'proficiency_level', 'personnel')
    search_fields = ('language_name', 'personnel__fullname')
    ordering = ('personnel', 'language_name', 'proficiency_level')
    autocomplete_fields = ['personnel']

    def get_language_display(self, obj):
        return obj.get_language_name_display()
    get_language_display.short_description = _("Til")

    def get_level_display(self, obj):
        return obj.get_proficiency_level_display()
    get_level_display.short_description = _("Daraja")


@admin.register(StateAward)
class StateAwardAdmin(admin.ModelAdmin):
    list_display = ('personnel', 'name', 'year', )
    list_filter = ('year', 'personnel')
    search_fields = ('name', 'personnel__fullname')
    ordering = ('-year', 'name')
    autocomplete_fields = ['personnel']

    class Media:
        css = {
            'all': ('admin/css/state_award.css',)
        }

@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ('personnel', 'workplace', 'position', 'start_date', 'end_date', 'get_duration')
    list_filter = ('start_date', 'end_date', 'personnel')
    search_fields = ('workplace', 'position', 'personnel__fullname')
    ordering = ('-start_date',)
    date_hierarchy = 'start_date'
    autocomplete_fields = ['personnel']

    def get_duration(self, obj):
        if obj.end_date:
            duration = obj.end_date - obj.start_date
            years = duration.days // 365
            months = (duration.days % 365) // 30
            return _("%(years)d yil %(months)d oy") % {'years': years, 'months': months}
        return _("Hozirgi kunda")
    get_duration.short_description = _("Ish davri")

    fieldsets = (
        (_('Asosiy ma’lumotlar'), {
            'fields': ('personnel', 'workplace', 'position')
        }),
        (_('Ish davri'), {
            'fields': ('start_date', 'end_date')
        }),
    )
