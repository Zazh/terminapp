from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Order, OrderItem
from cashflow.models import Transaction, Category


@receiver(post_save, sender=Order)
def handle_order_transaction(sender, instance, created, **kwargs):
    """
    Создаем транзакции при изменении статуса заказа.
    """
    if instance.status == 'completed':
        # Категория "Продажи на торг. точках" (ID = 3)
        sales_category = Category.objects.get(id=3)

        for item in instance.items.filter(status='completed'):
            Transaction.objects.update_or_create(
                order=instance,  # Устанавливаем связь с заказом
                category=sales_category,
                wallet=item.wallet,
                defaults={
                    'amount': item.calculate_amount(),
                    'date': instance.order_date,
                    'description': f"Доход от продажи {item.product.name} в заказе #{instance.id}",
                }
            )

    elif instance.status == 'cancelled':
        # Категория "Возвраты клиентам" (ID = 6)
        refund_category = Category.objects.get(id=6)

        for item in instance.items.all():
            Transaction.objects.create(
                order=instance,  # Устанавливаем связь с заказом
                category=refund_category,
                amount=-item.calculate_amount(),
                date=instance.order_date,
                description=f"Возврат за {item.product.name} в заказе #{instance.id}",
                wallet=item.wallet,
            )


@receiver(post_save, sender=OrderItem)
def handle_order_item_transaction(sender, instance, created, **kwargs):
    """
    Обрабатывает создание/обновление транзакций на основе статуса OrderItem.
    """
    # Удаляем транзакции, если статус становится "pending" или "cancelled"
    if instance.status in ['pending', 'cancelled']:
        Transaction.objects.filter(
            wallet=instance.wallet,
            description=f"Доход от продажи {instance.product.name} в заказе #{instance.order.id}"
        ).delete()
        return

    # Обрабатываем статус "completed"
    if instance.status == 'completed':
        sales_category = Category.objects.get(id=3)  # Категория для продаж
        Transaction.objects.get_or_create(
            transaction_type='income',
            category=sales_category,
            amount=instance.calculate_amount(),
            date=instance.order.order_date,
            description=f"Доход от продажи {instance.product.name} в заказе #{instance.order.id}",
            wallet=instance.wallet,
        )

    # Обрабатываем статус "refund"
    elif instance.status == 'refund':
        refund_category = Category.objects.get(id=6)  # Категория для возвратов
        Transaction.objects.create(
            transaction_type='expense',
            category=refund_category,
            amount=-instance.calculate_amount(),  # Отрицательная сумма для расхода
            date=instance.order.order_date,
            description=f"Возврат за {instance.product.name} в заказе #{instance.order.id}",
            wallet=instance.wallet,
        )
