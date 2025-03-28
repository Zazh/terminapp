# services.py
from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Order, OrderItem
from products.models import Product
from cashflow.models import Wallet

def calculate_order_total(order: Order) -> Decimal:
    """
    Рассчитывает общую сумму заказа с учётом всех позиций и скидок.
    """
    total = Decimal('0.00')
    for item in order.order_items.all():
        total += item.calculate_amount()
    return total

def update_order_status(order: Order) -> str:
    """
    Обновляет статус заказа на основе статусов всех позиций.
    """
    items = order.order_items.all()
    # Если хотя бы одна позиция в 'pending', считаем, что заказ в процессе
    if items.filter(status='pending').exists():
        return 'pending'
    # Если все позиции 'paid', считаем заказ завершённым
    if items.filter(status='paid').count() == items.count():
        return 'completed'
    # Иначе пусть будет 'cancelled' или другой по вашему выбору
    return 'cancelled'

def recalc_order_total(order: Order) -> None:
    """
    Пересчитывает сумму заказа.
    """
    total = calculate_order_total(order)
    order.total_amount = total
    order.save(update_fields=['total_amount'])

def refresh_order(order: Order):
    """
    Пересчитывает и сохраняет сумму и статус заказа.
    """
    order.total_amount = calculate_order_total(order)
    order.status = update_order_status(order)
    order.save(update_fields=['total_amount', 'status'])

class OrderService:
    @staticmethod
    @transaction.atomic
    def create_order(client_id=None) -> Order:
        """
        Создаёт новый Order (без позиций). При необходимости
        можно дополнить другими полями.
        """
        order = Order.objects.create(
            client_id=client_id,
            status='pending',
            total_amount=Decimal('0.00')
        )
        return order

    @staticmethod
    @transaction.atomic
    def update_order(order_id: int, **kwargs) -> Order:
        """
        Обновление заказа — например, изменение клиента или других полей.
        """
        try:
            order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            raise ValidationError(f"Заказ с id={order_id} не найден.")

        for field, value in kwargs.items():
            if hasattr(order, field):
                setattr(order, field, value)

        order.save()
        refresh_order(order)  # пересчитываем сумму и статус после изменений
        return order

    @staticmethod
    @transaction.atomic
    def delete_order(order_id: int):
        """
        Удалить заказ (при необходимости также можно удалять транзакции,
        связанные с order_items, но обычно это делается через каскад).
        """
        try:
            order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            raise ValidationError(f"Заказ с id={order_id} не найден.")
        order.delete()


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
        status: str = 'pending',
    ) -> OrderItem:
        """
        Создаёт новую позицию в заказе.
        """
        from products.models import PriceList  # если нужно динамически брать цену

        try:
            order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            raise ValidationError(f"Order с id={order_id} не найден.")

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            raise ValidationError(f"Product с id={product_id} не найден.")

        # Если цена не передана, берём последнюю из PriceList
        if price is None:
            price_list = product.price_list.order_by('-created_at').first()
            if price_list:
                price = price_list.price
            else:
                raise ValidationError(f"У продукта {product.name} (ID: {product.id}) нет цены.")

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
            wallet=wallet,
            status=status
        )

        # Пересчитываем заказ
        recalc_order_total(order)

        return order_item

    @staticmethod
    @transaction.atomic
    def update_order_item(order_item_id: int, **kwargs) -> OrderItem:
        """
        Обновить существующую позицию заказа.
        """
        try:
            order_item = OrderItem.objects.get(pk=order_item_id)
        except OrderItem.DoesNotExist:
            raise ValidationError(f"OrderItem с id={order_item_id} не найден.")

        # Обновляем поля
        for field, value in kwargs.items():
            if field == "discount" and value is None:
                value = Decimal("0.00")
            if field == "price" and value is None:
                raise ValidationError("Цена товара не может быть None.")

            if hasattr(order_item, field):
                setattr(order_item, field, value)

        order_item.save()

        # После обновления пересчитываем заказ
        recalc_order_total(order_item.order)

        return order_item

    @staticmethod
    @transaction.atomic
    def delete_order_item(order_item_id: int):
        """
        Удалить позицию заказа.
        """
        try:
            order_item = OrderItem.objects.get(pk=order_item_id)
        except OrderItem.DoesNotExist:
            raise ValidationError(f"OrderItem с id={order_item_id} не найден.")

        order = order_item.order
        order_item.delete()
        # Пересчитать заказ после удаления позиции
        recalc_order_total(order)