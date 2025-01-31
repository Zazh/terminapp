# hr/signals.py

from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import Employee
from .services import sync_user_groups

@receiver(post_save, sender=Employee)
def update_user_groups_on_employee_save(sender, instance, created, **kwargs):
    """
    После сохранения Employee вызываем сервис
    для синхронизации групп пользователя
    согласно ролям (roles) и статусу сотрудника.
    """
    sync_user_groups(instance)


@receiver(m2m_changed, sender=Employee.roles.through)
def update_user_groups_on_role_change(action, instance, **kwargs):
    """
    Когда меняются роли (M2M), пересинхронизируем группы пользователя.
    """
    if action in ('post_add', 'post_remove', 'post_clear'):
        sync_user_groups(instance)
