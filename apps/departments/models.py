from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

class DepartmentType(models.Model):
    name = models.CharField(_("Bo‘lim turi"), max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Bo‘lim turi")
        verbose_name_plural = _("Bo‘lim turlari")
        ordering = ['name']

class Department(models.Model):
    type = models.ForeignKey(
        DepartmentType, 
        verbose_name=_("Bo‘lim turi"),
        on_delete=models.PROTECT,
        related_name='departments'
    )
    name = models.CharField(_("Bo‘lim nomi"), max_length=255)

    def __str__(self):
        return f"{self.name} ({self.type.name})"

    class Meta:
        verbose_name = _("Bo‘lim")
        verbose_name_plural = _("Bo‘limlar")
        ordering = ['type', 'name']
        unique_together = ['type', 'name']

class Position(models.Model):
    department = models.ForeignKey(
        Department, 
        verbose_name=_("Bo‘lim"),
        on_delete=models.CASCADE,
        related_name='positions'
    )
    name = models.CharField(_("Lavozim nomi"), max_length=255)
    number_of_jobs = models.PositiveIntegerField(
        _("Shtat birligi soni"),
        help_text=_("Ushbu lavozimdagi mavjud shtat birliklari soni")
    )

    def __str__(self):
        return f"{self.name} ({self.department.name})"

    class Meta:
        verbose_name = _("Lavozim")
        verbose_name_plural = _("Lavozimlar")
        ordering = ['department', 'name']
        unique_together = ['department', 'name']

    def clean(self):
        if self.number_of_jobs < 1:
            raise ValidationError({
                'number_of_jobs': _("Shtat birligi soni 0 dan katta bo‘lishi kerak")
            })