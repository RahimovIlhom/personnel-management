from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from apps.core.models import BaseModel, phone_validator
from datetime import date
from django.core.validators import RegexValidator

User = get_user_model()


class PersonnelStatusHistory(BaseModel):
    personnel = models.ForeignKey(
        'Personnel',
        verbose_name=_("Xodim"),
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    old_status = models.CharField(_("Oldingi holat"), max_length=255)
    new_status = models.CharField(_("Yangi holat"), max_length=255)
    changed_by = models.ForeignKey(
        User,
        verbose_name=_("O‘zgartirgan foydalanuvchi"),
        on_delete=models.SET_NULL,
        null=True
    )
    reason = models.TextField(_("O‘zgartirish sababi"))

    def __str__(self):
        return f"{self.personnel} - {self.old_status} → {self.new_status}"

    class Meta:
        verbose_name = _("Holat tarixi")
        verbose_name_plural = _("Holat tarixlari")
        ordering = ['-created_at']


class Personnel(BaseModel):
    TYPE_CHOICES = [
        ('CANDIDATE', _('Nomzod')),
        ('EMPLOYEE', _('Xodim')),
    ]

    CANDIDATE_STATUS_CHOICES = [
        ('submitted', _('Topshirilgan')),
        ('accepted', _('Qabul qilingan')),
        ('rejected', _('Rad etilgan')),
    ]

    EMPLOYEE_STATUS_CHOICES = [
        ('working', _('Ishlamoqda')),
        ('left', _('Ishdan ketgan')),
        ('vacation', _('Ta\'tilda')),
    ]

    GENDER_CHOICES = [
        ('male', _('Erkak')),
        ('female', _('Ayol')),
    ]

    # Asosiy ma’lumotlar
    type = models.CharField(
        _("Turi"),
        max_length=255,
        choices=TYPE_CHOICES,
        default='EMPLOYEE'
    )
    status = models.CharField(
        _("Holati"),
        max_length=255,
        default='working'
    )
    position = models.ForeignKey(
        'departments.Position',
        verbose_name=_("Lavozimi"),
        on_delete=models.PROTECT,
        related_name='personnel'
    )
    fullname = models.CharField(_("To‘liq ismi"), max_length=255)

    # Shaxsiy ma’lumotlar
    birthdate = models.DateField(
        verbose_name=_("Tug‘ilgan sanasi")
    )
    birthplace = models.ForeignKey(
        'core.District',
        verbose_name=_("Tug‘ilgan joyi"),
        on_delete=models.PROTECT,
        related_name='birth_personnel'
    )
    nationality = models.ForeignKey(
        'core.Nation',
        verbose_name=_("Millati"),
        on_delete=models.PROTECT
    )
    gender = models.CharField(_("Jinsi"), max_length=10, choices=GENDER_CHOICES)
    pinfl = models.CharField(
        _("PINFL"),
        max_length=14,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{14}$',
                message=_("PINFL 14 ta raqamdan iborat bo‘lishi kerak")
            )
        ]
    )
    passport = models.CharField(
        _("Passport"),
        max_length=9,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Z]{2}\d{7}$',
                message=_("Passport seriyasi va raqami noto‘g‘ri formatda (AA1234567)")
            )
        ]
    )

    # Aloqa ma’lumotlari
    place_of_residence = models.ForeignKey(
        'core.District',
        verbose_name=_("Yashash joyi"),
        on_delete=models.PROTECT,
        related_name='resident_personnel'
    )
    address_of_residence = models.CharField(_("Manzili"), max_length=255)
    phone_number = models.CharField(
        _("Telefon raqami"),
        max_length=13,
        validators=[phone_validator]
    )
    additional_phone = models.CharField(
        _("Qo‘shimcha telefon"),
        max_length=13,
        null=True,
        blank=True,
        validators=[phone_validator]
    )

    # Ta’lim
    education_level = models.ForeignKey(
        'core.EducationLevel',
        verbose_name=_("Ta’lim darajasi"),
        on_delete=models.PROTECT
    )
    bachelor_university = models.CharField(
        _("Bakalavr universiteti"),
        max_length=255,
        null=True,
        blank=True
    )
    bachelor_graduation_year = models.IntegerField(
        _("Bakalavr tugatgan yili"),
        null=True,
        blank=True
    )
    master_university = models.CharField(
        _("Magistratura universiteti"),
        max_length=255,
        null=True,
        blank=True
    )
    master_graduation_year = models.IntegerField(
        _("Magistratura tugatgan yili"),
        null=True,
        blank=True
    )

    # Ilmiy ma’lumotlar
    academic_degree = models.ForeignKey(
        'core.AcademicDegree',
        verbose_name=_("Ilmiy daraja"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    academic_specialization = models.ForeignKey(
        'core.AcademicSpecialization',
        verbose_name=_("Ilmiy yo‘nalish"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    academic_title = models.ForeignKey(
        'core.AcademicTitle',
        verbose_name=_("Ilmiy unvon"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    academic_title_date = models.DateField(
        _("Ilmiy unvon berilgan sana"),
        null=True,
        blank=True
    )

    # Qo‘shimcha ma’lumotlar
    resume = models.FileField(
        _("Rezyume"),
        upload_to='resumes/',
        help_text=_("PDF formatida")
    )

    # Ish vaqti
    hired_date = models.DateField(_("Ishga qabul qilingan sana"), null=True, blank=True)
    left_date = models.DateField(_("Ishdan ketgan sana"), null=True, blank=True)

    def __str__(self):
        return f"{self.fullname}"

    class Meta:
        verbose_name = _("Xodim")
        verbose_name_plural = _("Xodimlar")
        ordering = ['fullname']
        indexes = [
            models.Index(fields=['type', 'status']),
            models.Index(fields=['pinfl']),
            models.Index(fields=['passport']),
        ]

    def clean(self):
        # Holat tekshiruvi
        if self.type == 'CANDIDATE' and self.status not in [choice[0] for choice in self.CANDIDATE_STATUS_CHOICES]:
            raise ValidationError({
                'status': _("Nomzod uchun noto‘g‘ri holat tanlangan")
            })
        if self.type == 'EMPLOYEE' and self.status not in [choice[0] for choice in self.EMPLOYEE_STATUS_CHOICES]:
            raise ValidationError({
                'status': _("Xodim uchun noto‘g‘ri holat tanlangan")
            })

        # Sana tekshiruvlari
        if self.hired_date and self.left_date and self.left_date < self.hired_date:
            raise ValidationError({
                'left_date': _("Ishdan ketgan sana ishga kirgan sanadan oldin bo‘lishi mumkin emas")
            })

        # Ta’lim ma’lumotlari tekshiruvi
        current_year = date.today().year
        if self.bachelor_graduation_year and self.bachelor_graduation_year > current_year:
            raise ValidationError({
                'bachelor_graduation_year': _("Bakalavr tugatgan yili kelgusi yil bo‘lishi mumkin emas")
            })
        if self.master_graduation_year and self.master_graduation_year > current_year:
            raise ValidationError({
                'master_graduation_year': _("Magistratura tugatgan yili kelgusi yil bo‘lishi mumkin emas")
            })
        if self.master_graduation_year and self.bachelor_graduation_year and \
                self.master_graduation_year <= self.bachelor_graduation_year:
            raise ValidationError({
                'master_graduation_year': _("Magistratura tugatgan yili bakalavr tugatgan yilidan keyin bo‘lishi kerak")
            })

    def save(self, force_type=None, *args, **kwargs):
        # Status o'zgarishi uchun argumentlarni ajratib olish
        changed_by = kwargs.pop('changed_by', None)
        status_change_reason = kwargs.pop('status_change_reason', '')

        if not self.pk:  # Yangi obyekt
            old_status = self.status
        else:
            old_obj = Personnel.objects.get(pk=self.pk)
            old_status = old_obj.status

        # Agar force_type berilgan bo'lsa, type'ni o'zgartirish
        if force_type:
            self.type = force_type

        # Asosiy saqlash
        super().save(*args, **kwargs)

        # Status o'zgargan bo'lsa
        if old_status != self.status:
            # Agar xodim ishdan ketgan bo'lsa va sabab ko'rsatilmagan bo'lsa
            if self.status == 'left' and not status_change_reason:
                raise ValidationError(_("Xodim ishdan ketganda sababini ko'rsatish shart!"))

            PersonnelStatusHistory.objects.create(
                personnel=self,
                old_status=old_status,
                new_status=self.status,
                changed_by=changed_by,
                reason=status_change_reason if status_change_reason else _("Status o'zgartirildi")
            )

    def convert_to_employee(self, initial_status='working'):
        """Nomzodni xodimga o'tkazish"""
        if self.type == 'EMPLOYEE':
            raise ValidationError(_("Bu foydalanuvchi allaqachon xodim!"))

        if self.status != 'accepted':
            raise ValidationError(_("Faqat qabul qilingan nomzodlarni xodimga o'tkazish mumkin!"))

        # Status o'zgarishini saqlash
        old_status = self.status
        self.status = initial_status
        self.type = 'EMPLOYEE'

        # O'zgarishlarni saqlash (force_type bilan)
        self.save(force_type='EMPLOYEE', status_change_reason=_("Nomzod xodimga o‘tkazildi"))

    @property
    def age(self):
        """Xodimning yoshini hisoblash"""
        if self.birthdate:
            today = date.today()
            age = today.year - self.birthdate.year
            # Tug'ilgan kun hali kelmagan bo'lsa 1 yil ayirish
            if today.month < self.birthdate.month or \
                    (today.month == self.birthdate.month and today.day < self.birthdate.day):
                age -= 1
            return age
        return None

    @property
    def experience_years(self):
        """Ish tajribasini yillarda hisoblash"""
        if self.hired_date:
            end_date = self.left_date or date.today()
            years = end_date.year - self.hired_date.year
            if end_date.month < self.hired_date.month or \
                    (end_date.month == self.hired_date.month and end_date.day < self.hired_date.day):
                years -= 1
            return years
        return 0


# Proxy modellar
class Employee(Personnel):
    class Meta:
        proxy = True
        verbose_name = _('Xodim')
        verbose_name_plural = _('Xodimlar')

    def save(self, *args, **kwargs):
        if not kwargs.get('force_type'):  # force_type berilmagan bo'lsa
            self.type = 'EMPLOYEE'
        super().save(*args, **kwargs)

class Candidate(Personnel):
    class Meta:
        proxy = True
        verbose_name = _('Nomzod')
        verbose_name_plural = _('Nomzodlar')

    def save(self, *args, **kwargs):
        if not kwargs.get('force_type'):  # force_type berilmagan bo'lsa
            self.type = 'CANDIDATE'
        super().save(*args, **kwargs)
