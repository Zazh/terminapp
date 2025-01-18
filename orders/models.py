from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal

from cashflow.models import Wallet, Transaction, Category
from products.models import Product
from clients.models import Client  # импорт вашей модели клиента

from django.contrib.contenttypes.models import ContentType

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'В процессе'),
        ('completed', 'Завершён'),
        ('cancelled', 'Отменён'),
    ]

    client = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Клиент",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Статус"
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Сумма заказа"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def get_total_amount(self) -> Decimal:
        """
        Возвращает сумму заказа, вычисляя её через все связанные OrderItem.
        (У заказа есть related_name="order_items" у ForeignKey в OrderItem)
        """
        total = Decimal('0.00')
        for item in self.order_items.all():
            total += item.calculate_amount()
        return total

    def __str__(self):
        return f"Заказ №{self.pk} (Клиент: {self.client})"

class OrderItem(models.Model):
    STATUS_CHOICES = [
        ('pending', 'В процессе'),
        ('paid', 'Оплачен'),
        ('cancelled', 'Отменен'),
        ('deleted', 'Удален'),
    ]

    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        verbose_name="Продукт",
        related_name="order_items"
    )
    quantity = models.PositiveIntegerField(verbose_name="Количество")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена",
        help_text="Цена за единицу продукта"
    )
    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Скидка",
        help_text="Скидка на единицу продукта (в денежном выражении)"
    )
    wallet = models.ForeignKey(
        'cashflow.Wallet',
        on_delete=models.SET_NULL,
        verbose_name="Кошелёк",
        null=True,
        blank=True,
        help_text="Кошелёк для транзакции"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Статус"
    )
    order = models.ForeignKey(
        'Order',
        on_delete=models.CASCADE,
        related_name="order_items",
        verbose_name="Заказ",
        null=True,
        blank=True
    )

    def clean(self):
        """
        Проверяет и устанавливает обязательные значения перед сохранением,
        а также валидирует данные.
        """
        super().clean()

        # Если цена не указана, но есть продукт
        if not self.price and self.product:
            self.price = self.product.price

        # Пример валидации скидки
        if self.discount < 0:
            raise ValidationError("Скидка не может быть отрицательной.")

        if self.discount > self.price:
            raise ValidationError("Скидка не может превышать цену.")

        # Если статус "Оплачен", кошелёк обязателен
        if self.status == 'paid' and not self.wallet:
            raise ValidationError("При статусе 'Оплачен' необходимо указать кошелёк.")

    def save(self, *args, **kwargs):
        """
        Создаёт или удаляет транзакцию при изменении статуса.
        """
        # Устанавливаем цену из связанного продукта, если она не задана.
        if not self.price and self.product:
            self.price = self.product.price

        super().save(*args, **kwargs)

        # Логика создания или удаления транзакции
        if self.status == 'paid':
            self.create_transaction()
        elif self.status in ['deleted']:
            self.delete_transaction()

    def create_transaction(self):
        """
        Создаёт или обновляет транзакцию для завершённого элемента заказа (продажа).
        """
        from cashflow.models import Transaction, Category  # Предполагается, что эти модели есть

        sales_category = Category.objects.get(id=3)  # Пример: категория "Продажи"
        content_type = ContentType.objects.get_for_model(OrderItem)

        Transaction.objects.update_or_create(
            content_type=content_type,
            object_id=self.pk,           # Связь через GenericForeignKey
            defaults={
                'category': sales_category,
                'wallet': self.wallet,
                'amount': self.calculate_amount(),
                'description': f"Продажа {self.product.name}, кол-во: {self.quantity}",
            },
        )

    def delete_transaction(self):
        """
        Удаляет транзакцию, связанную с этим элементом заказа.
        """
        from cashflow.models import Transaction
        from django.contrib.contenttypes.models import ContentType

        content_type = ContentType.objects.get_for_model(OrderItem)
        Transaction.objects.filter(
            content_type=content_type,
            object_id=self.pk
        ).delete()

    def calculate_amount(self):
        """
        Рассчитывает сумму элемента заказа с учётом скидки.
        Если скидка больше или равна цене, то итоговая цена считается равной 0.
        """
        net_price = self.price - self.discount
        if net_price < 0:
            net_price = Decimal('0.00')
        return self.quantity * net_price

    def __str__(self):
        wallet_name = self.wallet.name if self.wallet else 'No Wallet'
        return f"{self.product.name} x {self.quantity} ({wallet_name})"


class OrderItemRefund(models.Model):
    order_item = models.ForeignKey(
        'OrderItem',
        on_delete=models.CASCADE,
        related_name='refunds',
        verbose_name='Позиция заказа'
    )
    refund_date = models.DateField(auto_now_add=True, verbose_name='Дата возврата')
    reason = models.TextField(blank=True, verbose_name='Причина возврата')

    refund_quantity = models.PositiveIntegerField(verbose_name='Количество к возврату')
    refund_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Сумма возврата'
    )
    wallet = models.ForeignKey(
        'cashflow.Wallet',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name='Кошелёк для возврата'
    )

    def clean(self):
        super().clean()
        # Проверяем, что refund_quantity не больше, чем в order_item
        if self.refund_quantity > self.order_item.quantity:
            raise ValidationError("Нельзя вернуть больше, чем было куплено.")

        # Проверяем, что позиция заказа действительно оплачена
        if self.order_item.status != 'paid':
            raise ValidationError("Возврат возможен только для оплаченных позиций.")

        # Дополнительная проверка при необходимости: refund_amount <= сумма покупки
        # ...

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.create_refund_transaction()

    def create_refund_transaction(self):
        """
        Создает/обновляет транзакцию в cashflow для возврата.
        """
        from cashflow.models import Transaction, Category
        from django.contrib.contenttypes.models import ContentType

        # Допустим, что в Category есть категория с id=4 для "Возвраты"
        refund_category = Category.objects.get(id=4)
        content_type = ContentType.objects.get_for_model(OrderItemRefund)

        Transaction.objects.update_or_create(
            content_type=content_type,
            object_id=self.pk,  # Привязка к самой модели OrderItemRefund
            defaults={
                'category': refund_category,
                'wallet': self.wallet,
                'amount': self.refund_amount,
                'description': f"Возврат за {self.order_item.product.name} (кол-во: {self.refund_quantity})",
            }
        )

    def __str__(self):
        return f"Refund for {self.order_item} (qty: {self.refund_quantity})"