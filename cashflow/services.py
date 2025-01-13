from django.db.models import Sum, Case, When, F, DecimalField, Value
from django.db.models.functions import ExtractMonth, ExtractYear, Coalesce
from collections import defaultdict
from .models import Transaction
from datetime import date, timedelta, datetime
from typing import Dict, Optional
import decimal

def parse_transaction_filters(request) -> Dict[str, Optional[any]]:
    """
    Парсинг параметров фильтрации из запроса.
    """
    period = request.GET.get('period')
    exact_date_str = request.GET.get('exact_date')
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    transaction_type = request.GET.get('transaction_type')
    wallet_id = request.GET.get('wallet_id')
    category_id = request.GET.get('category_id')
    amount_min_str = request.GET.get('amount_min')
    amount_max_str = request.GET.get('amount_max')
    desc_substr = request.GET.get('desc')

    # Преобразование параметров
    try:
        exact_date = datetime.strptime(exact_date_str, "%Y-%m-%d").date() if exact_date_str else None
    except ValueError:
        exact_date = None

    try:
        s_date = datetime.strptime(start_date_str, "%Y-%m-%d").date() if start_date_str else None
        e_date = datetime.strptime(end_date_str, "%Y-%m-%d").date() if end_date_str else None
    except ValueError:
        s_date, e_date = None, None

    return {
        'period': period,
        'exact_date': exact_date,
        'start_date': s_date,
        'end_date': e_date,
        'transaction_type': transaction_type,
        'wallet_id': int(wallet_id) if wallet_id and wallet_id.isdigit() else None,
        'category_id': int(category_id) if category_id and category_id.isdigit() else None,
        'amount_min': float(amount_min_str) if amount_min_str else None,
        'amount_max': float(amount_max_str) if amount_max_str else None,
        'description_substring': desc_substr,
    }

def get_filtered_transactions(
    period=None,
    start_date=None,
    end_date=None,
    exact_date=None,
    transaction_type=None,
    wallet_id=None,
    category_id=None,
    amount_min=None,
    amount_max=None,
    description_substring=None,
):
    """
    Фильтрует QuerySet Transaction на основании заданных параметров.
    """
    qs = Transaction.objects.select_related('category', 'wallet').all()

    # Словарь фильтров
    filters = {
        'date': exact_date,
        'transaction_type': transaction_type,
        'wallet_id': wallet_id,
        'category_id': category_id,
        'amount__gte': amount_min,
        'amount__lte': amount_max,
    }
    # Убираем пустые значения
    filters = {key: value for key, value in filters.items() if value is not None}

    qs = qs.filter(**filters)

    # Фильтрация по дате
    if period:
        d_start, d_end = get_date_range_for_period(period, start_date, end_date)
        if d_start and d_end:
            qs = qs.filter(date__range=[d_start, d_end])
        elif d_start:
            qs = qs.filter(date__gte=d_start)
        elif d_end:
            qs = qs.filter(date__lte=d_end)

    # Вычисление общей суммы
    total_sum = qs.aggregate(total=Sum('amount'))['total'] or 0

    # Сортировка по убыванию даты
    return qs.order_by('-date', '-id'), total_sum


def get_date_range_for_period(period: str, custom_start=None, custom_end=None):
    """
    Возвращает диапазон дат на основании заданного периода.
    """
    today = date.today()

    if period == 'today':
        return today, today
    elif period == 'yesterday':
        y = today - timedelta(days=1)
        return y, y
    elif period == 'last_7_days':
        return today - timedelta(days=7), today
    elif period == 'last_30_days':
        return today - timedelta(days=30), today
    elif period == 'all_time':
        return None, None
    elif period == 'custom':
        return custom_start, custom_end

    return None, None


def get_wallet_balances():
    """
    Возвращает баланс по каждому кошельку.
    """
    return Transaction.calculate_wallet_balances()


def get_monthly_in_out(year: int):
    """
    Возвращает доходы и расходы по месяцам для заданного года.
    """
    return Transaction.monthly_summary(year)


def get_cashflow_summary_by_activity(year: int = None):
    """
    Возвращает сводку доходов/расходов в разрезе видов деятельности.
    """
    return Transaction.summary_by_activity(year)


def get_monthly_cashflow_by_category(year: int = None):
    """
    Возвращает месячный кэшфлоу по категориям за указанный год.
    """
    return Transaction.monthly_cashflow_by_category(year)


def get_last_12_year_months():
    """
    Возвращает список (year, month) для последних 12 месяцев.
    """
    today = date.today()
    return [
        (
            (today.year if today.month > i else today.year - 1),
            (today.month - i - 1) % 12 + 1
        )
        for i in range(12)
    ]


def get_activity_category_month_report_12():
    """
    Возвращает pivot-отчёт за последние 12 месяцев.
    """
    return Transaction.pivot_activity_category_last_12_months()


def get_all_transactions(year: int = None):
    """
    Возвращает все транзакции, отфильтрованные по году.
    """
    qs = Transaction.objects.select_related('category', 'wallet').order_by('-date')
    if year:
        qs = qs.filter(date__year=year)
    return qs
