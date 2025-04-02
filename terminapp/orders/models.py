from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal
from cashflow.models import Transaction, Category
from clients.models import Client
from django.contrib.contenttypes.models import ContentType
from hr.models import Company


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'В процессе'),
        ('completed', 'Завершён'),
        ('cancelled', 'Отменён'),
    ]
    '''
    инкапсуляция данных происходит через company
    '''
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
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
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    product = models.ForeignKey(
        'products.Product',  # Обновлено: теперь ссылается на Product
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
        Order,
        on_delete=models.CASCADE,
        related_name="order_items",
        verbose_name="Заказ"
    )

    def clean(self):
        super().clean()

        # Устанавливаем цену, если её нет
        if self.price is None and self.product:
            self.price = self.product.get_current_price()

        # Если цена все равно None, устанавливаем 0
        price = self.price if self.price is not None else Decimal("0.00")
        discount = self.discount if self.discount is not None else Decimal("0.00")

        if discount < 0:
            raise ValidationError("Скидка не может быть отрицательной.")

        if discount > price:
            raise ValidationError("Скидка не может превышать цену.")

        if self.status == 'paid' and not self.wallet:
            raise ValidationError("При статусе 'Оплачен' необходимо указать кошелёк.")

    def save(self, *args, **kwargs):
        if not self.price and self.product:
            self.price = self.product.get_current_price()
        super().save(*args, **kwargs)

        if self.status == 'paid':
            self.create_transaction()
        elif self.status in ['deleted']:
            self.delete_transaction()

    def create_transaction(self):

        # Пример: выбирается категория "Продажи" с id=3
        sales_category = Category.objects.get(id=3)
        content_type = ContentType.objects.get_for_model(OrderItem)

        Transaction.objects.update_or_create(
            content_type=content_type,
            object_id=self.pk,
            defaults={
                'company': self.wallet.company,
                'category': sales_category,
                'wallet': self.wallet,
                'amount': self.calculate_amount(),
                'description': f"Продажа {self.product.name}, кол-во: {self.quantity}",
            },
        )

    def delete_transaction(self):
        from cashflow.models import Transaction
        content_type = ContentType.objects.get_for_model(OrderItem)
        Transaction.objects.filter(
            content_type=content_type,
            object_id=self.pk
        ).delete()

    def calculate_amount(self):
        net_price = self.price - self.discount
        if net_price < 0:
            net_price = Decimal('0.00')
        return self.quantity * net_price

    def __str__(self):
        wallet_name = self.wallet.name if self.wallet else 'No Wallet'
        return f"{self.product.name} x {self.quantity} ({wallet_name})"


class OrderItemRefund(models.Model):
    order_item = models.ForeignKey(
        OrderItem,
        on_delete=models.CASCADE,
        related_name='refunds',
        verbose_name='Позиция заказа'
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
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
        null=True,
        blank=True,
        verbose_name='Кошелёк для возврата'
    )

    def clean(self):
        super().clean()
        if self.refund_quantity > self.order_item.quantity:
            raise ValidationError("Нельзя вернуть больше, чем было куплено.")

        if self.order_item.status != 'paid':
            raise ValidationError("Возврат возможен только для оплаченных позиций.")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.create_refund_transaction()

    def create_refund_transaction(self):
        from cashflow.models import Transaction, Category
        content_type = ContentType.objects.get_for_model(OrderItemRefund)
        refund_category = Category.objects.get(id=4)  # Пример: категория "Возвраты"
        Transaction.objects.update_or_create(
            content_type=content_type,
            object_id=self.pk,
            defaults={
                'company': self.wallet.company,
                'category': refund_category,
                'wallet': self.wallet,
                'amount': self.refund_amount,
                'description': f"Возврат за {self.order_item.product.name} (кол-во: {self.refund_quantity})",
            }
        )

    def __str__(self):
        return f"Refund for {self.order_item} (qty: {self.refund_quantity})"