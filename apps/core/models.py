from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

phone_validator = RegexValidator(
    regex=r'^\+?998?\d{9}$',
    message=_("Telefon raqam +998 bilan boshlanishi va 9 ta raqamdan iborat bo‘lishi kerak")
)


class BaseModel(models.Model):
    created_at = models.DateTimeField(_("Yaratilgan vaqti"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Yangilangan vaqti"), auto_now=True)

    class Meta:
        abstract = True


class Region(models.Model):
    name = models.CharField(_("Viloyat nomi"), max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Viloyat")
        verbose_name_plural = _("Viloyatlar")
        ordering = ['name']


class District(models.Model):
    region = models.ForeignKey(
        Region,
        verbose_name=_("Viloyat"),
        on_delete=models.CASCADE,
        related_name='districts'
    )
    name = models.CharField(_("Tuman nomi"), max_length=255)

    def __str__(self):
        return f"{self.name}, {self.region.name}"

    class Meta:
        verbose_name = _("Tuman")
        verbose_name_plural = _("Tumanlar")
        ordering = ['region', 'name']


class Nation(models.Model):
    name = models.CharField(_("Millat nomi"), max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Millat")
        verbose_name_plural = _("Millatlar")
        ordering = ['name']


class EducationLevel(models.Model):
    name = models.CharField(_("Ta’lim darajasi"), max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Ta’lim darajasi")
        verbose_name_plural = _("Ta’lim darajalari")
        ordering = ['name']


class AcademicDegree(models.Model):
    name = models.CharField(_("Ilmiy daraja nomi"), max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Ilmiy daraja")
        verbose_name_plural = _("Ilmiy darajalar")
        ordering = ['name']


class AcademicSpecialization(models.Model):
    name = models.CharField(_("Ilmiy yo‘nalish nomi"), max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Ilmiy yo‘nalish")
        verbose_name_plural = _("Ilmiy yo‘nalishlar")
        ordering = ['name']


class AcademicTitle(models.Model):
    name = models.CharField(_("Ilmiy unvon nomi"), max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Ilmiy unvon")
        verbose_name_plural = _("Ilmiy unvonlar")
        ordering = ['name']


class LanguageProficiency(models.Model):
    LEVELS = [
        ('A1', 'A1 - Boshlang‘ich'),
        ('A2', 'A2 - Boshlang‘ich+'),
        ('B1', 'B1 - O‘rta'),
        ('B2', 'B2 - O‘rta+'),
        ('C1', 'C1 - Yuqori'),
        ('C2', 'C2 - Mukammal'),
    ]

    personnel = models.ForeignKey(
        'personnel.Personnel',
        verbose_name=_("Xodim"),
        on_delete=models.CASCADE,
        related_name='languages'
    )
    language_name = models.CharField(_("Til nomi"), max_length=255)
    proficiency_level = models.CharField(
        _("Bilish darajasi"),
        max_length=2,
        choices=LEVELS
    )

    def __str__(self):
        return f"{self.personnel} - {self.get_language_name_display()} - {self.get_proficiency_level_display()}"

    class Meta:
        verbose_name = _("Til bilish darajasi")
        verbose_name_plural = _("Til bilish darajalari")
        ordering = ['language_name', 'proficiency_level']
        unique_together = ['language_name', 'proficiency_level']


class StateAward(models.Model):
    personnel = models.ForeignKey(
        'personnel.Personnel',
        verbose_name=_("Xodim"),
        on_delete=models.CASCADE,
        related_name='awards'
    )
    name = models.CharField(_("Mukofot nomi"), max_length=255)
    year = models.IntegerField(_("Berilgan yili"))

    def __str__(self):
        return f"{self.personnel} - {self.name} ({self.year})"

    class Meta:
        verbose_name = _("Davlat mukofoti")
        verbose_name_plural = _("Davlat mukofotlari")
        ordering = ['-year', 'name']
        unique_together = ['personnel', 'name', 'year']


class WorkExperience(models.Model):
    personnel = models.ForeignKey(
        'personnel.Personnel',
        verbose_name=_("Xodim"),
        on_delete=models.CASCADE,
        related_name='work_experiences'
    )
    workplace = models.CharField(_("Ish joyi"), max_length=255)
    position = models.CharField(_("Lavozimi"), max_length=255)
    start_date = models.DateField(_("Ishga kirgan sanasi"))
    end_date = models.DateField(_("Ishdan ketgan sanasi"), null=True, blank=True)

    def __str__(self):
        return f"{self.personnel}: {self.position} - {self.workplace}"

    class Meta:
        verbose_name = _("Ish tajribasi")
        verbose_name_plural = _("Ish tajribalari")
        ordering = ['-start_date']

    def clean(self):
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError({
                'end_date': _("Ishdan ketgan sana ishga kirgan sanadan oldin bo'lishi mumkin emas")
            })
