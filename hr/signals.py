# hr/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Employee
from .services import sync_user_groups

@receiver(post_save, sender=Employee)
def update_user_groups_on_employee_save(sender, instance, **kwargs):
    """
    После сохранения Employee вызываем сервис
    для синхронизации групп пользователя
    согласно Role и статусу сотрудника.
    """
    sync_user_groups(instance)
