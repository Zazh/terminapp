from decimal import Decimal
from .models import Order, OrderItem
from django.db import transaction
from products.models import Product, PriceList  # Импорт обновлённой модели продукта
from cashflow.models import Wallet
from django.core.exceptions import ValidationError


def calculate_order_total(order):
    """
    Рассчитывает общую сумму заказа.
    """
    total = Decimal('0.00')
    # Используем order.order_items вместо order.items
    for item in order.order_items.all():
        total += item.calculate_amount()
    return total


def recalc_order_total(order: Order) -> None:
    """
    Сервисная функция, которая пересчитывает сумму заказа
    и обновляет поле total_amount в БД.
    """
    total = order.get_total_amount()
    order.total_amount = total
    order.save(update_fields=['total_amount'])


def update_order_status(order):
    """
    Обновляет статус заказа.
    """
    items = order.order_items.all()
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


class OrderItemService:
    @staticmethod
    @transaction.atomic
    def create_order_item(
            order_id: int,
            product_id: int,
            quantity: int,
            price: Decimal = None,
            discount: Decimal = Decimal('0.00'),
            wallet_id: int = None,
            status: str = 'pending'
    ) -> OrderItem:
        """
        Создать OrderItem. Если цена не передана, берём её из Product
        """
        try:
            order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            raise ValidationError(f"Order с id={order_id} не найден.")

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            raise ValidationError(f"Product с id={product_id} не найден.")

        # Если цена не передана, берем актуальную цену из Product
        if price is None:
            price_list = product.price_list.order_by('-created_at').first()  # Получаем последнюю актуальную цену
            if price_list:
                price = price_list.price  # Берем значение цены
            else:
                price = 0  # Значение по умолчанию, если нет цен

        wallet = None
        if wallet_id:
            try:
                wallet = Wallet.objects.get(pk=wallet_id)
            except Wallet.DoesNotExist:
                raise ValidationError(f"Wallet с id={wallet_id} не найден.")

        order_item = OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=price,
            discount=discount,
            # При необходимости можно передавать wallet=wallet
            status=status
        )
        return order_item

    @staticmethod
    @transaction.atomic
    def update_order_item(order_item_id: int, **kwargs) -> OrderItem:
        """
        Обновить уже существующий OrderItem.
        Если в kwargs нет поля price, то его не изменяем.
        """
        try:
            order_item = OrderItem.objects.get(pk=order_item_id)
        except OrderItem.DoesNotExist:
            raise ValidationError(f"OrderItem с id={order_item_id} не найден.")

        # Обновляем поля, переданные в kwargs
        for field, value in kwargs.items():
            if hasattr(order_item, field):
                setattr(order_item, field, value)

        order_item.save()
        return order_item