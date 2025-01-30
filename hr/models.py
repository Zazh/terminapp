# hr/models.py

from django.db import models
from django.conf import settings
from django.contrib.auth.models import Group

STATUS_CHOICES = (
    ('ACTIVE', 'Active'),
    ('FIRED', 'Fired'),
    ('ON_LEAVE', 'On Leave'),
    # Добавляйте при необходимости другие статусы
)


class Department(models.Model):
    """
    Справочник департаментов
    """
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=50, unique=True, null=True, blank=True)

    class Meta:
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'

    def __str__(self):
        return self.name


class Role(models.Model):
    """
    Роль, привязанная к департаменту и Django Group (для прав).
    """
    name = models.CharField(max_length=255, unique=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='roles'
    )
    groups = models.ManyToManyField(
        Group,
        related_name='hr_roles',
        blank=True
    )

    class Meta:
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return f"{self.name} ({self.department.name})"


class Employee(models.Model):
    """
    Тонкая сущность, которая связывает:
    - Пользователя (User)
    - Роль (Role)
    - Статус сотрудника (активен, уволен и т.п.)

    А также определяем кастомные permissions, если нужны
    (как пример 'can_approve_vacation', 'can_manage_salaries')
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employee_profile'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees'
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
        # В кастомном User может не быть get_full_name(), поэтому используем username/email
        username_display = getattr(self.user, 'username', None) or getattr(self.user, 'email', '')
        role_name = self.role.name if self.role else 'No Role'
        return f"{username_display} - {role_name} ({self.get_status_display()})"


class EmployeeInfo(models.Model):
    """
    Дополнительная «карточка сотрудника» с подробными данными:
    - дата приёма
    - контакты
    - и т. д.

    Связь OneToOne с Employee, чтобы для каждого Employee
    были свои детальные поля, но при этом Employee
    оставался "тонкой" связью с User/Role.
    """
    employee = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE,
        related_name='info'
    )
    phone = models.CharField(max_length=20, blank=True, null=True)
    hire_date = models.DateField(blank=True, null=True)

    # Можно добавить любые другие поля: адрес, дата рождения и т. д.

    class Meta:
        verbose_name = 'Employee Info'
        verbose_name_plural = 'Employees Info'

    def __str__(self):
        return f"Info for {self.employee}"
