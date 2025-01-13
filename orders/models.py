from django.db import models
from django.db.models import Sum, Case, When, F, DecimalField
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from cashflow.models import Wallet, Transaction, Category


class Order(models.Model):
    customer = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name="orders")
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, editable=False)  # Поле недоступно для редактирования
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'В ожидании'),
            ('completed', 'Завершен'),
            ('cancelled', 'Отменен'),
        ],
        default='pending'
    )

    def __str__(self):
        return f"Order #{self.id} - {self.customer.first_name} ({self.total_amount})"

    def calculate_total_amount(self):
        """
        Пересчитывает общую сумму заказа на основе элементов заказа.
        """
        # Если объект ещё не имеет primary key, возвращаем текущую сумму
        if not self.pk:
            return self.total_amount

        total = sum(item.calculate_amount() for item in self.items.all())
        return total

    def save(self, *args, **kwargs):
        """
        Автоматически обновляет поле `total_amount` перед сохранением.
        """
        super().save(*args, **kwargs)  # Сначала сохраняем объект, чтобы получить primary key
        self.total_amount = self.calculate_total_amount()
        super().save(update_fields=['total_amount'])  # Сохраняем обновлённое значение `total_amount`

    def update_status_and_total(self):
        """
        Обновляет статус заказа и общую сумму на основе статусов и цен OrderItem.
        """
        items = self.items.all()
        if items.exists():
            # Обновляем общую сумму
            self.total_amount = items.aggregate(
                total=Sum(F('quantity') * F('price'), output_field=DecimalField())
            )['total'] or 0.00

            # Определяем статус на основе статусов элементов
            if items.filter(status='pending').exists():
                self.status = 'pending'
            elif items.filter(status='completed').count() == items.count():
                self.status = 'completed'
            else:
                self.status = 'cancelled'
        else:
            self.total_amount = 0.00
            self.status = 'pending'
        self.save()


class OrderItem(models.Model):
    STATUS_CHOICES = [
        ('pending', 'В ожидании'),
        ('completed', 'Завершен'),
        ('refunded', 'Возврат средств'),
        ('cancelled', 'Отменен'),
    ]

    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Кошелек"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    def save(self, *args, **kwargs):
        # Устанавливаем цену из продукта, если она не задана
        if not self.price:
            self.price = self.product.price

        # Проверяем переход в статус "Возврат средств"
        if self.status == 'refunded' and not self._can_refund():
            raise ValueError("Возврат средств возможен только для завершенных заказов.")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} x {self.quantity} ({self.wallet.name if self.wallet else 'No Wallet'})"

    def calculate_amount(self):
        return self.quantity * self.price

    def _can_refund(self):
        """
        Проверяет, возможен ли возврат средств (только если статус был 'completed').
        """
        return self.__class__.objects.filter(pk=self.pk, status='completed').exists()


# Сигналы для автоматического обновления Order
@receiver(post_save, sender=OrderItem)
def update_order_on_item_save(sender, instance, **kwargs):
    """
    Обновляет статус и сумму заказа, когда сохраняется OrderItem.
    """
    if instance.order:
        instance.order.update_status_and_total()
