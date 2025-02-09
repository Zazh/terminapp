# cashflow/models.py
from django.db import models
from django.db.models import Sum, Case, When, F, DecimalField, Value
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class WalletQuerySet(models.QuerySet):
    def annotate_balance(self):
        return self.annotate(
            balance=Sum(
                Case(
                    When(
                        transactions__category__operation_type__in=['income', 'technical_income'],
                        then=F('transactions__amount')
                    ),
                    When(
                        transactions__category__operation_type__in=['expense', 'technical_expense'],
                        then=-F('transactions__amount')
                    ),
                    default=Value(0),
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                )
            )
        )

class Wallet(models.Model):
    """
    Кошелёк, содержащий средства.
    """
    objects = WalletQuerySet.as_manager()  # Важно!
    name = models.CharField("Название кошелька", max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return self.name

class ActivityType(models.Model):
    """
    Вид деятельности (Операционная, Инвестиционная, Финансовая, Техническая операция и т.д.)
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name



class Category(models.Model):
    OPERATION_TYPES = [
        ('income', 'Поступление'),
        ('expense', 'Выбытие'),
        ('technical_income', 'Техническое поступление'),
        ('technical_expense', 'Техническое выбытие'),
    ]

    name = models.CharField("Название статьи", max_length=255)
    description = models.TextField("Описание статьи", blank=True, null=True)
    operation_type = models.CharField(
        max_length=20,
        choices=OPERATION_TYPES,
        verbose_name="Тип операции",
        help_text="Указывает, как обрабатывать эту категорию"
    )
    activity_type = models.ForeignKey(
        'ActivityType',
        on_delete=models.CASCADE,
        related_name="categories",
        verbose_name="Вид деятельности",
        null=True,
        blank=True,
        help_text="Укажите вид деятельности для данной категории"
    )

    def __str__(self):
        return self.name


class Transaction(models.Model):
    """
    Финансовая транзакция (доход/расход).
    """
    category = models.ForeignKey(
        'cashflow.Category',
        on_delete=models.CASCADE,
        related_name="transactions",
        verbose_name="Категория"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    wallet = models.ForeignKey(
        'cashflow.Wallet',
        on_delete=models.CASCADE,
        related_name="transactions",
        verbose_name="Кошелёк",
        default=1,  # Укажите ID кошелька по умолчанию (или удалите, если не нужно)
    )

    # ----------- Начало полей GenericForeignKey -----------
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    reason_transaction = GenericForeignKey('content_type', 'object_id')
    # ----------- Конец полей GenericForeignKey -----------

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    @property
    def transaction_type(self):
        """
        Определяет тип транзакции (income/expense) на основе категории.
        """
        operation_type = self.category.operation_type  # Предполагается, что у Category есть поле operation_type
        if operation_type in ['income', 'technical_income']:
            return 'Доход'
        elif operation_type in ['expense', 'technical_expense']:
            return 'Расход'
        return 'Не определено'

    @classmethod
    def calculate_wallet_balances(cls):
        """
        Возвращает балансы по каждому кошельку.
        """
        return (
            cls.objects
            .values('wallet__name')
            .annotate(
                balance=Sum(
                    Case(
                        When(category__operation_type__in=['income', 'technical_income'], then=F('amount')),
                        When(category__operation_type__in=['expense', 'technical_expense'], then=-F('amount')),
                        output_field=DecimalField(),
                    )
                )
            )
            .order_by('wallet__name')
        )

    @property
    def signed_amount(self):
        """
        Возвращает сумму с учетом типа транзакции (расход — отрицательный).
        """
        if self.category.operation_type in ['expense', 'technical_expense']:
            return -self.amount
        return self.amount

    def __str__(self):
        return f"{self.transaction_type}: {self.amount} {self.category} ({self.wallet})"