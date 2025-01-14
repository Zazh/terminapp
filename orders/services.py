from decimal import Decimal
from django.db.models import Sum, F, DecimalField


def calculate_order_total(order):
    """
    Рассчитывает общую сумму заказа.
    """
    return order.items.aggregate(
        total=Sum(F('quantity') * F('price'), output_field=DecimalField())
    )['total'] or Decimal('0.00')


def update_order_status(order):
    """
    Обновляет статус заказа.
    """
    items = order.items.all()
    if items.filter(status='pending').exists():
        return 'pending'
    elif items.filter(status='completed').count() == items.count():
        return 'completed'
    return 'cancelled'


def refresh_order(order):
    """
    Пересчитывает сумму и статус заказа.
    """
    order.total_amount = calculate_order_total(order)
    order.status = update_order_status(order)
    order.save(update_fields=['total_amount', 'status'])
