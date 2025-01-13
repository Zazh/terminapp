from datetime import datetime
from django.shortcuts import render
from .models import Wallet, Category, Transaction
from .services import (
    get_filtered_transactions,
    parse_transaction_filters,
)


def transactions_list_view(request):
    """
    Вьюха для отображения списка транзакций с фильтром.
    """
    # Парсим параметры фильтрации
    filters = parse_transaction_filters(request)

    # Получаем транзакции и общую сумму
    transactions_qs, total_sum = get_filtered_transactions(**filters)

    wallets = Wallet.objects.all().order_by('name')
    categories = Category.objects.all().order_by('name')

    context = {
        'transactions': transactions_qs,
        'total_sum': total_sum,
        'categories': categories,
        'wallets': wallets,
    }
    return render(request, 'cashflow/transactions_list.html', context)


def wallet_balances_view(request):
    """
    Вьюха для отображения балансов кошельков.
    """
    wallet_data = Transaction.calculate_wallet_balances()
    context = {'wallets': wallet_data}
    return render(request, 'cashflow/wallet_balances.html', context)


def monthly_report_view(request):
    """
    Вьюха для отображения отчёта за указанный год.
    """
    year = request.GET.get('year')
    year = int(year) if year and year.isdigit() else datetime.now().year

    monthly_data = Transaction.monthly_summary(year)
    context = {
        'year': year,
        'months': monthly_data,
    }
    return render(request, 'cashflow/monthly_report.html', context)


def dashboard_view(request):
    """
    Основная «дашборд»-вьюха.
    """
    # Получаем год из GET-параметров
    year = request.GET.get('year')
    year = int(year) if year and year.isdigit() else None

    # Сбор данных для дашборда
    cashflow_data = Transaction.summary_by_activity(year)
    wallet_data = Transaction.calculate_wallet_balances()
    monthly_category_data = Transaction.monthly_cashflow_by_category(year)
    pivot_12_data = Transaction.pivot_activity_category_last_12_months()

    # Формируем контекст для шаблона
    context = {
        'cashflow_data': cashflow_data,
        'wallet_data': wallet_data,
        'monthly_category_data': monthly_category_data,
        'pivot_12_data': pivot_12_data,
    }

    return render(request, 'cashflow/dashboard.html', context)

def _add_months(base_date, months):
    """
    Утилита для добавления или вычитания месяцев из даты.
    """
    year = base_date.year
    month = base_date.month + months
    while month < 1:
        month += 12
        year -= 1
    while month > 12:
        month -= 12
        year += 1
    day = min(base_date.day, 28)
    return datetime.date(year, month, day)
