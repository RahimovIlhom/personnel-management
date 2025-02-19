from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = 'admin', _('Administrator')
        MANAGER = 'manager', _('Menejer')
        HR = 'hr', _('HR menejer')
        EMPLOYEE = 'employee', _('Xodim')

    role = models.CharField(
        _("Foydalanuvchi roli"),
        max_length=10,
        choices=Roles.choices,
        default=Roles.EMPLOYEE
    )

    class Meta:
        verbose_name = _("Foydalanuvchi")
        verbose_name_plural = _("Foydalanuvchilar")
        ordering = ['username']

    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name}"

    def __str__(self):
        return f"{self.get_role_display()} - {self.full_name}"
