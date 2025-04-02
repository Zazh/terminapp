# hr/services.py
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group
from hr.models import Company, Department, Role, Employee, EmployeeInfo


def create_company(owner, name, subdomain, billing_plan='BASE'):
    """
    Создает компанию для владельца.
    1. Проверяет, что у пользователя ещё нет компании.
    2. Создает объект Company.
    3. Автоматически создает базовый департамент (например, "Управленческий отдел").
    4. Создает роль "Администратор" с полным доступом, привязанную к базовому департаменту.
    5. Создает профиль сотрудника (Employee) для владельца и назначает ему роль "Администратор".
    6. Создает отдел Владельца".
    """
    # Проверяем, что пользователь еще не является владельцем компании.
    if hasattr(owner, 'company'):
        raise ValidationError("Пользователь уже владеет компанией.")

    # 1. Создаем компанию
    company = Company(
        owner=owner,
        name=name,
        subdomain=subdomain,
        billing_plan=billing_plan
    )
    company.full_clean()
    company.save()

    # 2. Создаем базовый департамент "Управленческий отдел"
    default_department = Department.objects.create(
        company=company,
        name="Управленческий отдел"
    )

    # 3. Создаем роль "Администратор" для компании,
    # привязываем ее к созданному департаменту
    admin_role = Role.objects.create(
        company=company,
        name="Администратор",
        department=default_department
    )

    # Получаем (или создаем) группу "administrator" и привязываем её к роли
    admin_group, _ = Group.objects.get_or_create(name="administrator")
    admin_role.groups.add(admin_group)

    # 4. Создаем профиль сотрудника для владельца
    employee = Employee.objects.create(
        company=company,
        user=owner,
        status='ACTIVE'
    )
    # 5. Назначаем владельцу роль "Администратор"
    employee.roles.add(admin_role)

    # 6. Создаем EmployeeInfo и связываем его с созданным Employee
    EmployeeInfo.objects.create(
        employee=employee,
        hire_date=employee.created_at.date()  # если хотите только дату
    )

    return company


