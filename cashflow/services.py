# cashflow/services.py

from django.db import transaction
from django.db.models import Sum
from datetime import date, timedelta, datetime
from typing import Dict, Optional, Tuple, Any, List
import decimal

from .models import Wallet, Transaction, Category
from hr.models import Company


def create_wallet(company: Company, name: str) -> Wallet:
    """
    Создает кошелёк, принадлежащий заданной компании.
    """
    return Wallet.objects.create(company=company, name=name)

@transaction.atomic
def create_transaction(
    company: Company,
    wallet: Wallet,
    category: Category,
    amount,
    description: str = "",
    reason_object=None
) -> Transaction:
    """
    Создаёт транзакцию в рамках заданной компании и кошелька.
    reason_object - произвольный объект (GenericForeignKey), если требуется.
    """
    if wallet.company_id != company.id:
        raise ValueError("Кошелёк принадлежит другой компании.")

    new_tx = Transaction(
        company=company,
        wallet=wallet,
        category=category,
        amount=amount,
        description=description
    )
    if reason_object:
        new_tx.reason_transaction = reason_object

    new_tx.save()
    return new_tx

def get_wallets_for_company(company: Company):
    """
    Возвращает QuerySet кошельков, принадлежащих конкретной компании,
    с аннотированным балансом.
    """
    return Wallet.objects.annotate_balance().filter(company=company)


def get_transactions_for_company(company: Company):
    """
    Возвращает QuerySet транзакций, принадлежащих конкретной компании.
    """
    return Transaction.objects.select_related('wallet', 'category').filter(company=company)


def parse_transaction_filters(request) -> Dict[str, Optional[Any]]:
    """
    Парсит GET-параметры запроса для фильтрации транзакций.
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
    company: Company,
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
) -> Tuple[Any, decimal.Decimal]:
    """
    Фильтрует QuerySet Transaction в рамках компании на основании параметров.
    Возвращает (queryset, total_sum).
    """
    qs = Transaction.objects.select_related('category', 'wallet')
    # Сначала фильтруем по company
    qs = qs.filter(company=company)

    # transaction_type => фильтр по category__operation_type
    if transaction_type:
        if transaction_type == 'income':
            qs = qs.filter(category__operation_type__in=['income', 'technical_income'])
        elif transaction_type == 'expense':
            qs = qs.filter(category__operation_type__in=['expense', 'technical_expense'])
        else:
            qs = qs.filter(category__operation_type=transaction_type)

    # Фильтр по exact_date
    if exact_date:
        qs = qs.filter(date=exact_date)

    # Фильтр по wallet_id / category_id
    if wallet_id:
        qs = qs.filter(wallet_id=wallet_id)
    if category_id:
        qs = qs.filter(category_id=category_id)

    # Фильтр по сумме
    if amount_min is not None:
        qs = qs.filter(amount__gte=amount_min)
    if amount_max is not None:
        qs = qs.filter(amount__lte=amount_max)

    # Фильтр по описанию (substring)
    if description_substring:
        qs = qs.filter(description__icontains=description_substring)

    # Фильтрация по периоду
    if period:
        d_start, d_end = get_date_range_for_period(period, start_date, end_date)
        if d_start and d_end:
            qs = qs.filter(date__range=[d_start, d_end])
        elif d_start:
            qs = qs.filter(date__gte=d_start)
        elif d_end:
            qs = qs.filter(date__lte=d_end)

    # Сумма
    total_sum = qs.aggregate(total=Sum('amount'))['total'] or decimal.Decimal('0.00')

    # Сортируем по убыванию даты
    qs = qs.order_by('-date', '-id')

    return qs, total_sum


def get_date_range_for_period(period: str, custom_start=None, custom_end=None):
    """
    Возвращает (start, end) на основании period.
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


def get_wallet_balances(company):
    """
    Возвращает баланс по каждому кошельку в рамках заданной компании.
    Использует класс-метод Transaction.calculate_wallet_balances().
    Если в модели не предусмотрен параметр company — 
    придётся отфильтровать вручную.
    """
    # Пример, если метод calculate_wallet_balances не учитывает компанию,
    # то фильтруем вручную:
    # Transaction.objects.filter(company=company).calculate_wallet_balances() 
    #
    # Но, если метод calculate_wallet_balances() внутри уже умеет работать
    # с company (или мы можем его переписать), то:
    return Transaction.calculate_wallet_balances().filter(company=company)


def get_monthly_in_out(company, year: int):
    """
    Возвращает доходы/расходы по месяцам за год для конкретной компании.
    Если Transaction.monthly_summary ожидает company, передаём:
        return Transaction.monthly_summary(company=company, year=year)
    Если нет, можно реализовать здесь вручную.
    """
    # Предположим, в модели Transaction есть метод monthly_summary(year, company)
    return Transaction.monthly_summary(year=year, company=company)


def get_cashflow_summary_by_activity(company, year: Optional[int] = None):
    """
    Возвращает сводку доходов/расходов в разрезе видов деятельности (activity_type),
    только для заданной компании.
    Если в Transaction.summary_by_activity() нет company,
    нужно доработать сам метод или вручную сделать агрегацию здесь.
    """
    return Transaction.summary_by_activity(year=year, company=company)


def get_monthly_cashflow_by_category(company, year: Optional[int] = None):
    """
    Возвращает месячный кэшфлоу по категориям за указанный год в рамках заданной компании.
    Аналогично, если Transaction.monthly_cashflow_by_category не принимает company,
    придётся реализовать вручную или доработать метод.
    """
    return Transaction.monthly_cashflow_by_category(year=year, company=company)


def get_last_12_year_months() -> List[Tuple[int, int]]:
    """
    Возвращает список (year, month) для последних 12 месяцев (без привязки к company).
    """
    today = date.today()
    return [
        (
            (today.year if today.month > i else today.year - 1),
            (today.month - i - 1) % 12 + 1
        )
        for i in range(12)
    ]


def get_activity_category_month_report_12(company):
    """
    Возвращает pivot-отчёт за последние 12 месяцев (по Activity/Category)
    в рамках заданной компании.
    Если Transaction.pivot_activity_category_last_12_months() не учитывает company,
    нужно доработать.
    """
    # Пример (если не учтён company):
    # return Transaction.pivot_activity_category_last_12_months().filter(company=company)
    return Transaction.pivot_activity_category_last_12_months(company=company)


def get_all_transactions(company, year: Optional[int] = None):
    """
    Возвращает все транзакции компании, при необходимости фильтрует по году.
    """
    qs = Transaction.objects.select_related('category', 'wallet').filter(company=company).order_by('-date')
    if year:
        qs = qs.filter(date__year=year)
    return qs