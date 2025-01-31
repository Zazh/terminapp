# hr/models.py

from django.db import models
from django.conf import settings
from django.contrib.auth.models import Group
from companys.models import Company  # Импорт из приложения tenant (companys)

STATUS_CHOICES = (
    ('ACTIVE', 'Active'),
    ('FIRED', 'Fired'),
    ('ON_LEAVE', 'On Leave'),
    # Добавляйте при необходимости другие статусы
)


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
    """
    "Сотрудник" (membership), привязывающий пользователя (User)
    к конкретной компании. Один user может быть сотрудником
    в нескольких компаниях, и иметь несколько ролей в одной.

    Множественные роли:
    Используем M2M на модель Role (roles).
    """
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='employees'
    )
    # ForeignKey, чтобы один пользователь мог иметь несколько Employee-записей (в разных компаниях)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employee_profiles'
    )
    # Вместо одного role — M2M, чтобы сотрудник мог иметь несколько ролей
    roles = models.ManyToManyField(
        Role,
        related_name='employees',
        blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )

    class Meta:
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
        permissions = (
            ('can_approve_vacation', 'Can approve vacation requests'),
            ('can_manage_salaries', 'Can manage salaries'),
        )

    def __str__(self):
        # В кастомном User может не быть get_full_name(), поэтому fallback на username/email
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
