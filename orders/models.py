from django.db import models
from cashflow.models import Wallet, Transaction, Category
from products.models import Product


class OrderItem(models.Model):
    STATUS_CHOICES = [
        ('pending', 'В ожидании'),
        ('completed', 'Завершен'),
        ('refunded', 'Возврат средств'),
        ('cancelled', 'Отменен'),
    ]

    product = models.ForeignKey(
        Product,
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
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Кошелёк",
        help_text="Кошелёк для транзакции"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Статус"
    )

    def save(self, *args, **kwargs):
        """
        Создаёт или удаляет транзакцию при изменении статуса.
        """
        # Устанавливаем цену из связанного продукта, если она не задана
        if not self.price and self.product:
            self.price = self.product.price

        super().save(*args, **kwargs)

        # Логика создания или удаления транзакции
        if self.status == 'completed':
            self.create_transaction()
        elif self.status in ['pending', 'cancelled', 'refunded']:
            self.delete_transaction()

    def create_transaction(self):
        """
        Создаёт или обновляет транзакцию для завершённого элемента заказа.
        """
        sales_category = Category.objects.get(id=3)  # Получите категорию "Продажи"
        Transaction.objects.update_or_create(
            order_item=self,
            defaults={
                'category': sales_category,
                'wallet': self.wallet,
                'amount': self.calculate_amount(),
                'description': f"Продажа {self.product.name}, количество: {self.quantity}",
            },
        )

    def delete_transaction(self):
        """
        Удаляет транзакцию, связанную с этим элементом заказа.
        """
        if hasattr(self, 'transaction'):
            self.transaction.delete()

    def calculate_amount(self):
        """
        Рассчитывает сумму элемента заказа.
        """
        return self.quantity * self.price

    def clean(self):
        """
        Проверяет и устанавливает обязательные значения перед сохранением.
        """
        if not self.price and self.product:
            self.price = self.product.price

    def __str__(self):
        return f"{self.product.name} x {self.quantity} ({self.wallet.name if self.wallet else 'No Wallet'})"
