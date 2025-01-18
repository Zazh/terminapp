# orders/signals.py
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .models import OrderItem

@receiver(pre_save, sender=OrderItem)
def orderitem_pre_save(sender, instance, **kwargs):
    # При сохранении объекта всегда вызываем 'full_clean', чтобы сработал 'clean()'
    try:
        instance.full_clean()
    except ValidationError as e:
        # Если возникли ошибки валидации, прерываем сохранение
        raise e