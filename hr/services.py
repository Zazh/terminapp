# hr/services.py

from .models import Employee


def sync_user_groups(employee: Employee):
    """
    Синхронизирует группы пользователя (User.groups)
    с группами, привязанными к Role сотрудника.
    Если Role нет или сотрудник уволен, то (по умолчанию) очищаем группы.

    При необходимости логику можно усложнить: если сотрудник
    "ON_LEAVE", оставить некоторые доступы и т. п.
    """
    user = employee.user
    role = employee.role

    if role and employee.status == 'ACTIVE':
        role_groups = role.groups.all()
        user.groups.set(role_groups)
    else:
        # Если роль не указана или сотрудник не "ACTIVE",
        # то очищаем все группы
        user.groups.clear()

    user.save()
