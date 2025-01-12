# cashflow/models.py

from django.db import models

class BusinessDirection(models.Model):
    """
    Направление бизнеса (Оптовое, Розница, Общее и т.д.)
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class ActivityType(models.Model):
    """
    Вид деятельности (Операционная, Инвестиционная, Финансовая, Техническая операция и т.д.)
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Group(models.Model):
    """
    Группа (Поступление, Выбытие и т.д.)
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    """
    Модель для учёта финансовых статей.
    """
    name = models.CharField("Название статьи", max_length=255)
    description = models.TextField("Описание статьи", blank=True, null=True)
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="categories",
        verbose_name="Группа",
    )
    activity_type = models.ForeignKey(
        ActivityType,
        on_delete=models.CASCADE,
        related_name="categories",
        verbose_name="Вид деятельности"
    )

    def __str__(self):
        return self.name


class Transaction(models.Model):
    """
    Транзакция, которая связывается с категорией,
    имеет сумму, дату, описание, кошелёк и т.д.
    """

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)

    wallet = models.ForeignKey(
        'Wallet',
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name='Кошелёк',
        null=True,
        blank=True
    )

    def __str__(self):
        # Для удобства показываем "Доход"/"Расход", исходя из группы
        return f"{self.get_transaction_type_display()}: {self.amount} {self.category} ({self.wallet})"

    @property
    def transaction_type(self):
        """
        Определяем тип транзакции на основании группы:
        - Если группа == "Поступление", считаем это 'income'
        - Если группа == "Выбытие", считаем это 'expense'
        - Иначе возвращаем None или другое значение (на случай, если появятся новые группы).
        """
        group_name = self.category.group.name if self.category and self.category.group else ""
        if group_name == "Поступление":
            return "income"
        elif group_name == "Выбытие":
            return "expense"
        # Можно добавить другие варианты групп, если понадобится
        return None

    def get_transaction_type_display(self):
        """
        Человеко-читаемое название.
        """
        if self.transaction_type == "income":
            return "Доход"
        elif self.transaction_type == "expense":
            return "Расход"
        return "Неизвестно"


class Wallet(models.Model):
    """
    Сущность «кошелёк» (счёт).
    Пример: 'Основной счёт', 'Кошелёк в рублях', 'Счёт в банке' и т.д.
    """
    name = models.CharField("Название кошелька", max_length=255, unique=True)
    # При желании можно хранить текущий баланс:
    #balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.name}"