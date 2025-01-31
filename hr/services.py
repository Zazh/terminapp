# hr/services.py

from django.contrib.auth.models import Group
from .models import Employee

def sync_user_groups(employee: Employee):
    """
    Синхронизирует группы пользователя (User.groups)
    со всеми группами, привязанными к Ролям (Role) сотрудника.
    Если ролей нет или сотрудник уволен (либо не активен),
    очищаем группы по умолчанию.

    При необходимости логику можно усложнить:
    - Если status == 'ON_LEAVE', оставить только часть групп и т. п.
    """
    user = employee.user
    roles_qs = employee.roles.all()

    if roles_qs.exists() and employee.status == 'ACTIVE':
        # Собираем все группы из всех ролей
        # Подразумевается, что у Role есть ManyToManyField к Group: role.groups
        # Можно сделать «глобальный» запрос через Group.objects.filter(...)
        all_role_groups = Group.objects.filter(hr_roles__in=roles_qs).distinct()
        user.groups.set(all_role_groups)
    else:
        # Если нет ролей или сотрудник не "ACTIVE", то очищаем все группы
        user.groups.clear()

    user.save()
