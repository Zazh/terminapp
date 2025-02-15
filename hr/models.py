# hr/models.py
import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re

PLAN_CHOICES = (
    ('TRIAL', 'Trail'),
    ('BASE', 'Base'),
)

STATUS_COMPANY_CHOICES = (
    ('ACTIVE', 'Active'),
    ('SUSPENDED', 'Suspended'),
    ('DELETED', 'DELETED'),
)

STATUS_EMPOLYEE_CHOICES = (
    ('ACTIVE', 'Active'),
    ('FIRED', 'Fired'),
    ('ON_LEAVE', 'On Leave'),
    # Добавляйте при необходимости другие статусы
)

class Company(models.Model):
    """
    Модель, отвечающая за компанию (Tenant).
    Каждый пользователь может создать только одну компанию, поэтому добавляем поле owner.
    """
    name = models.CharField(max_length=255, unique=True)
    subdomain = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        help_text=_("Введите поддомен, состоящий только из маленьких латинских букв, цифр и дефисов.")
    )
    billing_plan = models.CharField(
        max_length=50,
        default='BASE',
        choices = PLAN_CHOICES,
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_COMPANY_CHOICES,
        default='ACTIVE'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="company",
        verbose_name=_("Owner")
    )

    def clean(self):
        """
        Валидация перед сохранением.
        Если subdomain указан, убеждаемся, что он состоит только из маленьких букв, цифр и дефисов.
        """
        super().clean()
        if self.subdomain:
            regex_subdomain = r'^[a-z0-9-]+$'
            normalized = self.subdomain.lower().strip()
            if not re.match(regex_subdomain, normalized):
                raise ValidationError(_("Invalid subdomain format. It must contain only lowercase letters, numbers, and hyphens."))
            self.subdomain = normalized

    def __str__(self):
        return self.name


class Department(models.Model):
    """
    Справочник департаментов в рамках одной компании.
    """
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='departments'
    )
    # Убираем unique=True, чтобы Department "HR" мог существовать в разных компаниях
    name = models.CharField(max_length=255)
    # Аналогично для code, можно оставить уникальность глобально, если бизнес-требование такое:
    code = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        # Имя департамента не должно повторяться в рамках одной company
        unique_together = ('company', 'name')
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'

    def __str__(self):
        return f"{self.name} ({self.company.name})"


class Role(models.Model):
    """
    Роль, привязанная к компании (Tenant) и, при необходимости, к департаменту.
    Можно также хранить связь с Django Group для прав.
    """
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='roles'
    )
    # Снова убираем global unique=True, т.к. 'Manager' может встречаться в разных компаниях
    name = models.CharField(max_length=255)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='roles'
    )
    groups = models.ManyToManyField(
        Group,
        related_name='hr_roles',
        blank=True
    )

    class Meta:
        # Имя роли уникально в рамках одной компании
        unique_together = ('company', 'name')
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'

    def __str__(self):
        dep_info = f" / {self.department.name}" if self.department else ""
        return f"{self.name} ({self.company.name}{dep_info})"


class Employee(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='employees'
    )
    # Изменяем на OneToOneField, чтобы один пользователь мог иметь только один Employee,
    # то есть быть сотрудником только в одной компании.
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employee_profile'  # переименовали в единственное число
    )
    # Сотруднику по-прежнему можно назначать несколько ролей
    roles = models.ManyToManyField(
        Role,
        related_name='employees',
        blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_EMPOLYEE_CHOICES,
        default='ACTIVE'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
        permissions = (
            ('can_approve_vacation', 'Can approve vacation requests'),
            ('can_manage_salaries', 'Can manage salaries'),
        )

    def __str__(self):
        username_display = getattr(self.user, 'username', None) or getattr(self.user, 'email', '')
        return f"{username_display} @ {self.company.name} ({self.get_status_display()})"


class EmployeeInfo(models.Model):
    """
    Дополнительная "карточка сотрудника" с подробными данными:
    - дата приёма
    - контакты
    - и т. д.

    Связь OneToOne с Employee, чтобы хранить развернутые поля.
    """
    employee = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE,
        related_name='info'
    )
    phone = models.CharField(max_length=20, blank=True, null=True)
    hire_date = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name = 'Employee Info'
        verbose_name_plural = 'Employees Info'

    def __str__(self):
        return f"Info for {self.employee}"


INVITATION_STATUS = (
    ('PENDING', 'Pending'),
    ('ACCEPTED', 'Accepted'),
    ('EXPIRED', 'Expired'),
)

class EmployeeInvitation(models.Model):
    inviter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_invitations'
    )
    company = models.ForeignKey(
        'Company',
        on_delete=models.CASCADE,
        related_name='invitations'
    )
    email = models.EmailField()
    token = models.CharField(max_length=64, unique=True, editable=False)
    status = models.CharField(max_length=10, choices=INVITATION_STATUS, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.token:
            # Генерируем уникальный токен (например, с помощью uuid)
            self.token = uuid.uuid4().hex
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Invitation for {self.email} to {self.company.name}"