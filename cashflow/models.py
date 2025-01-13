from django.db import models
from django.db.models import Sum, Case, When, F, DecimalField
from django.db.models.functions import ExtractMonth, ExtractYear, Coalesce
from django.db.models import Value
from collections import defaultdict
from django.utils.timezone import now
import datetime
import decimal

class Wallet(models.Model):
    """
    Сущность "кошелёк" (счёт).
    Пример: 'Основной счёт', 'Кошелёк в рублях', 'Счёт в банке' и т.д.
    """
    name = models.CharField("Название кошелька", max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return self.name


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
    TRANSACTION_TYPES = [
        ('income', 'Доход'),
        ('expense', 'Расход'),
    ]

    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPES,
        verbose_name="Тип транзакции",
        blank = True,
        null = True
    )
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)
    wallet = models.ForeignKey(
        'Wallet',
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name="Кошелек",
        null=True,
        blank=True
    )

    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='transactions',
        null=True,  # Если транзакция может быть без заказа
        blank=True,  # Если поле не является обязательным
        verbose_name="Связанный заказ"
    )

    def save(self, *args, **kwargs):
        """
        Автоматически устанавливаем тип транзакции на основе группы категории.
        """
        if not self.transaction_type and self.category.operation_type:
            operation_type = self.category.operation_type
            if operation_type in ['income', 'technical_income']:
                self.transaction_type = 'income'
            elif operation_type in ['expense', 'technical_expense']:
                self.transaction_type = 'expense'
        super().save(*args, **kwargs)

    @property
    def signed_amount(self):
        """
        Возвращает сумму с учетом типа транзакции (расход — отрицательный).
        """
        if self.transaction_type == 'expense':
            return -self.amount
        return self.amount

    @classmethod
    def calculate_wallet_balances(cls):
        """
        Возвращает балансы по каждому кошельку.
        """
        return (
            cls.objects.values('wallet__name')
            .annotate(
                balance=Sum(
                    Case(
                        When(transaction_type='income', then=F('amount')),
                        When(transaction_type='expense', then=-F('amount')),
                        output_field=DecimalField(),
                    )
                )
            )
            .order_by('wallet__name')
        )

    @classmethod
    def monthly_summary(cls, year):
        """
        Возвращает доходы и расходы по месяцам за указанный год.
        """
        qs = cls.objects.filter(date__year=year)
        monthly_data = (
            qs.annotate(month=ExtractMonth('date'))
            .values('month')
            .annotate(
                income=Sum(
                    Case(
                        When(transaction_type='income', then=F('amount')),
                        default=Value(0),
                        output_field=DecimalField(),
                    )
                ),
                expense=Sum(
                    Case(
                        When(transaction_type='expense', then=F('amount')),
                        default=Value(0),
                        output_field=DecimalField(),
                    )
                )
            )
            .order_by('month')
        )

        return [
            {
                'month': month,
                'income': next((item['income'] for item in monthly_data if item['month'] == month), 0),
                'expense': next((item['expense'] for item in monthly_data if item['month'] == month), 0),
            }
            for month in range(1, 13)
        ]

    @classmethod
    def summary_by_activity(cls, year=None):
        """
        Возвращает сводку доходов/расходов в разрезе видов деятельности.
        """
        qs = cls.objects.all()
        if year:
            qs = qs.filter(date__year=year)

        return {
            'details': list(
                qs.values(activity_type=F('category__activity_type__name'))  # Группировка по activity_type
                .annotate(
                    income=Coalesce(
                        Sum(
                            Case(
                                When(transaction_type='income', then=F('amount')),
                                default=Value(0),
                                output_field=DecimalField(),
                            )
                        ),
                        Value(0, output_field=DecimalField())
                    ),
                    expense=Coalesce(
                        Sum(
                            Case(
                                When(transaction_type='expense', then=-F('amount')),
                                default=Value(0),
                                output_field=DecimalField(),
                            )
                        ),
                        Value(0, output_field=DecimalField())
                    ),
                    net_flow=Coalesce(
                        Sum(
                            Case(
                                When(transaction_type='income', then=F('amount')),
                                When(transaction_type='expense', then=-F('amount')),
                                default=Value(0),
                                output_field=DecimalField(),
                            )
                        ),
                        Value(0, output_field=DecimalField())
                    ),
                )
                .order_by('activity_type')
            ),
            'total': qs.aggregate(
                income=Coalesce(
                    Sum(
                        Case(
                            When(transaction_type='income', then=F('amount')),
                            default=Value(0),
                            output_field=DecimalField(),
                        )
                    ),
                    Value(0, output_field=DecimalField())
                ),
                expense=Coalesce(
                    Sum(
                        Case(
                            When(transaction_type='expense', then=-F('amount')),
                            default=Value(0),
                            output_field=DecimalField(),
                        )
                    ),
                    Value(0, output_field=DecimalField())
                ),
                net_flow=Coalesce(
                    Sum(
                        Case(
                            When(transaction_type='income', then=F('amount')),
                            When(transaction_type='expense', then=-F('amount')),
                            default=Value(0),
                            output_field=DecimalField(),
                        )
                    ),
                    Value(0, output_field=DecimalField())
                ),
            ),
        }

    @classmethod
    def monthly_cashflow_by_category(cls, year=None):
        """
        Возвращает месячный кэшфлоу по категориям за указанный год.
        """
        qs = cls.objects.all()
        if year:
            qs = qs.filter(date__year=year)

        annotated_data = (
            qs.annotate(month=ExtractMonth('date'))
            .values('month', 'category__name')
            .annotate(
                net_flow=Coalesce(
                    Sum(
                        Case(
                            When(transaction_type='income', then=F('amount')),
                            When(transaction_type='expense', then=-F('amount')),
                            default=Value(0),
                            output_field=DecimalField(),
                        )
                    ),
                    Value(0, output_field=DecimalField())
                )
            )
            .order_by('month', 'category__name')
        )

        # Преобразуем данные в структуру для шаблона
        result = defaultdict(lambda: {'categories': [], 'total_net_flow': 0})

        for row in annotated_data:
            month = row['month']
            result[month]['categories'].append({
                'category': row['category__name'],
                'net_flow': row['net_flow'],
            })
            result[month]['total_net_flow'] += row['net_flow']

        return {
            'details': [
                {'month': month, **details}
                for month, details in sorted(result.items())
            ],
            'grand_total_net_flow': sum(details['total_net_flow'] for details in result.values()),
        }

    @classmethod
    def pivot_activity_category_last_12_months(cls):
        """
        Возвращает pivot-отчёт за последние 12 месяцев.
        """
        today = datetime.date.today()
        last_12_months = [
            ((today.year if today.month > i else today.year - 1), (today.month - i - 1) % 12 + 1)
            for i in range(12)
        ]
        allowed_pairs = set(last_12_months)

        qs = (
            cls.objects.filter(
                date__year__gte=min(y for y, _ in last_12_months),
                date__year__lte=max(y for y, _ in last_12_months),
            )
            .annotate(year=ExtractYear('date'), month=ExtractMonth('date'))
            .values('year', 'month', 'category__operation_type',
                    'category__name')  # Заменено 'activity_type' на 'operation_type'
            .annotate(
                net_flow=Coalesce(
                    Sum(
                        Case(
                            When(transaction_type='income', then=F('amount')),
                            When(transaction_type='expense', then=-F('amount')),
                            default=Value(0),
                            output_field=DecimalField(),
                        )
                    ),
                    Value(0, output_field=DecimalField())
                )
            )
        )

        data = defaultdict(lambda: defaultdict(lambda: defaultdict(decimal.Decimal)))
        for row in qs:
            year, month = row['year'], row['month']
            if (year, month) in allowed_pairs:
                data[row['category__operation_type']][row['category__name']][(year, month)] += row['net_flow']

        result_data = [
            {
                'operation_type': operation_type,
                'categories': [
                    {
                        'category': category,
                        'year_month_data': [
                            {
                                'year': year,
                                'month': month,
                                'net_flow': months.get((year, month), 0),
                            }
                            for year, month in last_12_months
                        ],
                    }
                    for category, months in categories.items()
                ],
            }
            for operation_type, categories in data.items()
        ]

        return {
            'data': result_data,
            'periods': last_12_months,
        }

    def __str__(self):
        wallet_name = self.wallet.name if self.wallet else 'No Wallet'
        return f"{self.get_transaction_type_display()}: {self.amount} {self.category} ({wallet_name})"

