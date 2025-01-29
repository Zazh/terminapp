from cashflow.models import Transaction, Category, Wallet
from django.db.models import Sum, Case, When, F, DecimalField, Value, Q
from django.db.models.functions import ExtractMonth, ExtractYear
from collections import defaultdict
from datetime import date, timedelta
from typing import Optional, Dict
from django.db.models import QuerySet  # Добавьте этот импорт

import decimal


def _apply_filters(qs: QuerySet, filters: Dict) -> QuerySet:
    """Применяет фильтры к QuerySet"""
    if start_date := filters.get('start_date'):
        qs = qs.filter(date__gte=start_date)
    if end_date := filters.get('end_date'):
        qs = qs.filter(date__lte=end_date)
    if wallet_id := filters.get('wallet_id'):
        qs = qs.filter(wallet_id=wallet_id)
    if category_id := filters.get('category_id'):
        qs = qs.filter(category_id=category_id)
    if activity_type := filters.get('activity_type'):
        qs = qs.filter(category__activity_type__name=activity_type)
    return qs


def get_cashflow_data(
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        wallet_id: Optional[int] = None,
        category_id: Optional[int] = None,
        activity_type: Optional[str] = None
) -> Dict:
    """
    Сводка движения денежных средств с фильтрацией
    """
    qs = _apply_filters(
        Transaction.objects.all(),
        {'start_date': start_date, 'end_date': end_date,
         'wallet_id': wallet_id, 'category_id': category_id,
         'activity_type': activity_type}
    )

    data = qs.values(
        activity_type=F('category__activity_type__name')
    ).annotate(
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
        'details': [{
            'activity_type': item['activity_type'],
            'income': item['income'] or 0,
            'expense': item['expense'] or 0,
            'net_flow': item['net_flow'] or 0
        } for item in data],
        'total': {
            'income': total['income'] or 0,
            'expense': total['expense'] or 0,
            'net_flow': total['net_flow'] or 0
        }
    }


def get_monthly_category_data(
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        wallet_id: Optional[int] = None,
        activity_type: Optional[str] = None
) -> Dict:
    """
    Месячный кэшфлоу по категориям с фильтрацией
    """
    qs = _apply_filters(
        Transaction.objects.all(),
        {'start_date': start_date, 'end_date': end_date,
         'wallet_id': wallet_id, 'activity_type': activity_type}
    )

    monthly_data = qs.annotate(
        month=ExtractMonth('date'),
        year=ExtractYear('date')
    ).values(
        'year', 'month', 'category__name'
    ).annotate(
        net_flow=Sum(
            Case(
                When(category__operation_type__in=['income', 'technical_income'], then=F('amount')),
                When(category__operation_type__in=['expense', 'technical_expense'], then=-F('amount')),
                default=Value(0),
                output_field=DecimalField(),
            )
        )
    ).order_by('year', 'month')

    result = defaultdict(lambda: defaultdict(lambda: {'categories': [], 'total_net_flow': 0}))

    for item in monthly_data:
        key = f"{item['year']}-{item['month']}"
        result[key]['categories'].append({
            'category': item['category__name'],
            'net_flow': item['net_flow']
        })
        result[key]['total_net_flow'] += item['net_flow']

    return {
        'details': dict(result),
        'grand_total_net_flow': sum(
            month_data['total_net_flow']
            for year_data in result.values()
            for month_data in year_data.values()
        )
    }


def get_pivot_12_data(
        end_date: Optional[date] = None,
        wallet_id: Optional[int] = None,
        category_id: Optional[int] = None
) -> Dict:
    """
    Pivot-отчёт по Activity Types за период
    """
    end_date = end_date or date.today()
    start_date = end_date - timedelta(days=365)

    qs = _apply_filters(
        Transaction.objects.filter(
            date__range=(start_date, end_date)
        ),
        {'wallet_id': wallet_id, 'category_id': category_id}
    )

    pivot_data = qs.annotate(
        year=ExtractYear('date'),
        month=ExtractMonth('date')
    ).values(
        'year', 'month',
        'category__activity_type__name',
        'category__name'
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

    # Обработка и группировка данных остается без изменений
    ...


def get_wallet_data(
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        wallet_id: Optional[int] = None
) -> Dict:
    """
    Балансы кошельков с фильтрацией
    """
    qs = _apply_filters(
        Transaction.objects.all(),
        {'start_date': start_date, 'end_date': end_date, 'wallet_id': wallet_id}
    )

    return (
        qs.values('wallet__name')
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


def get_all_transactions(
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        wallet_id: Optional[int] = None,
        category_id: Optional[int] = None,
        activity_type: Optional[str] = None
) -> tuple[QuerySet, decimal.Decimal]:
    """
    Возвращает отфильтрованные транзакции и общую сумму
    """
    qs = _apply_filters(
        Transaction.objects.select_related('wallet', 'category'),
        {'start_date': start_date, 'end_date': end_date,
         'wallet_id': wallet_id, 'category_id': category_id,
         'activity_type': activity_type}
    ).order_by('-date')

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