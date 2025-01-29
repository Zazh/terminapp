# analytics/services.py

from cashflow.models import Transaction, Category, Wallet
from django.db.models import Sum, Case, When, F, DecimalField, Value
from django.db.models.functions import ExtractMonth, ExtractYear
from collections import defaultdict
from datetime import date
import decimal


def get_cashflow_data():
    """
    Сводка движения денежных средств по видам деятельности.
    """
    qs = Transaction.objects.all()
    data = qs.values(activity_type=F('category__activity_type__name')).annotate(
        income=Sum(
            Case(
                When(category__operation_type__in=['income', 'technical_income'], then=F('amount')),
                default=Value(0),
                output_field=DecimalField(),
            )
        ),
        expense=Sum(
            Case(
                When(category__operation_type__in=['expense', 'technical_expense'], then=F('amount')),
                default=Value(0),
                output_field=DecimalField(),
            )
        ),
        net_flow=Sum(
            Case(
                When(category__operation_type__in=['income', 'technical_income'], then=F('amount')),
                When(category__operation_type__in=['expense', 'technical_expense'], then=-F('amount')),
                default=Value(0),
                output_field=DecimalField(),
            )
        ),
    )
    total = qs.aggregate(
        income=Sum(
            Case(
                When(category__operation_type__in=['income', 'technical_income'], then=F('amount')),
                default=Value(0),
                output_field=DecimalField(),
            )
        ),
        expense=Sum(
            Case(
                When(category__operation_type__in=['expense', 'technical_expense'], then=F('amount')),
                default=Value(0),
                output_field=DecimalField(),
            )
        ),
        net_flow=Sum(
            Case(
                When(category__operation_type__in=['income', 'technical_income'], then=F('amount')),
                When(category__operation_type__in=['expense', 'technical_expense'], then=-F('amount')),
                default=Value(0),
                output_field=DecimalField(),
            )
        ),
    )
    return {
        'details': [
            {
                'activity_type': item['activity_type'],  # Используем алиас
                'income': item['income'],
                'expense': item['expense'],
                'net_flow': item['net_flow']
            }
            for item in data
        ],
        'total': {
            'income': total['income'] or 0,
            'expense': total['expense'] or 0,
            'net_flow': total['net_flow'] or 0
        }
    }



def get_monthly_category_data():
    """
    Месячный кэшфлоу по категориям.
    """
    qs = Transaction.objects.annotate(month=ExtractMonth('date')).values('month', 'category__name').annotate(
        net_flow=Sum(
            Case(
                When(category__operation_type__in=['income', 'technical_income'], then=F('amount')),
                When(category__operation_type__in=['expense', 'technical_expense'], then=-F('amount')),

                default=Value(0),
                output_field=DecimalField(),
            )
        )
    )
    monthly_data = {}
    for item in qs:
        month = item['month']
        if month not in monthly_data:
            monthly_data[month] = {'categories': [], 'total_net_flow': 0}
        monthly_data[month]['categories'].append({
            'category': item['category__name'],
            'net_flow': item['net_flow']
        })
        monthly_data[month]['total_net_flow'] += item['net_flow']

    grand_total = sum(data['total_net_flow'] for data in monthly_data.values())
    return {'details': monthly_data, 'grand_total_net_flow': grand_total}


def get_pivot_12_data():
    """
    Возвращает Pivot-отчёт по Activity Types за последние 12 месяцев.
    """
    from django.db.models.functions import ExtractYear, ExtractMonth

    today = date.today()
    last_12_months = [
        ((today.year if today.month > i else today.year - 1), (today.month - i - 1) % 12 + 1)
        for i in range(12)
    ]

    qs = Transaction.objects.filter(
        date__year__gte=min(y for y, _ in last_12_months),
        date__year__lte=max(y for y, _ in last_12_months),
    ).annotate(
        year=ExtractYear('date'),
        month=ExtractMonth('date')
    ).values(
        'year', 'month', 'category__activity_type__name', 'category__name'
    ).annotate(
        net_flow=Sum(
            Case(
                When(category__operation_type__in=['income', 'technical_income'], then=F('amount')),
                When(category__operation_type__in=['expense', 'technical_expense'], then=-F('amount')),
                default=Value(0),
                output_field=DecimalField(),
            )
        )
    )

    data = defaultdict(lambda: defaultdict(lambda: defaultdict(decimal.Decimal)))

    # Группируем данные по Activity Type, Category, Year-Month
    for row in qs:
        year, month = row['year'], row['month']
        activity_type = row['category__activity_type__name']
        category_name = row['category__name']
        data[activity_type][category_name][(year, month)] += row['net_flow']

    # Подготавливаем данные для шаблона
    result_data = [
        {
            'activity_type': activity_type,
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
        for activity_type, categories in data.items()
    ]

    return {'data': result_data, 'periods': last_12_months}


def get_wallet_data():
    """
    Балансы кошельков.
    """
    return Transaction.calculate_wallet_balances()


def get_all_transactions():
    """
    Возвращает все транзакции и их общую сумму.
    """
    qs = Transaction.objects.select_related('wallet', 'category').order_by('-date')

    # Вычисление общей суммы с учётом типа транзакции
    total_sum = qs.aggregate(
        total=Sum(
            Case(
                When(category__operation_type__in=['income', 'technical_income'], then=F('amount')),
                When(category__operation_type__in=['expense', 'technical_expense'], then=-F('amount')),
                default=Value(0),
                output_field=DecimalField(),
            )
        )
    )['total'] or 0

    return qs, total_sum