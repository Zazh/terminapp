# cashflow/views.py

from datetime import datetime
from django.shortcuts import render
from .models import Wallet, Category
from .services import (get_wallet_balances,
                       get_monthly_in_out,
                       get_cashflow_summary_by_activity,
                       get_monthly_cashflow_by_category,
                       get_filtered_transactions,
                       get_activity_category_month_report_12)

def transactions_list_view(request):
    """
    Вьюха для отображения списка транзакций с фильтром.
    Списки кошельков и категорий передаём в шаблон,
    чтобы пользователь мог выбирать по имени (или ID).
    """

    # 1. Получаем списки кошельков и категорий (для выпадающих списков).
    #    Сортируем по имени, чтобы упорядоченно отображать в <select>.
    wallets = Wallet.objects.all().order_by('name')
    categories = Category.objects.all().order_by('name')

    # 2. Считываем GET-параметры
    period = request.GET.get('period')             # 'today', 'yesterday', ...
    exact_date_str = request.GET.get('exact_date') # '2025-01-01', etc.
    start_date_str = request.GET.get('start_date') # для custom
    end_date_str = request.GET.get('end_date')     # для custom

    transaction_type = request.GET.get('transaction_type')  # 'income', 'expense', 'transfer'
    wallet_id = request.GET.get('wallet_id')
    category_id = request.GET.get('category_id')
    amount_min_str = request.GET.get('amount_min')
    amount_max_str = request.GET.get('amount_max')
    desc_substr = request.GET.get('desc')

    # 3. Преобразуем строки в нужные типы (даты, int, float)
    exact_date = None
    if exact_date_str:
        try:
            exact_date = datetime.strptime(exact_date_str, "%Y-%m-%d").date()
        except ValueError:
            pass

    s_date = None
    if start_date_str:
        try:
            s_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        except ValueError:
            pass

    e_date = None
    if end_date_str:
        try:
            e_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            pass

    # wallet_id и category_id преобразуем в int
    if wallet_id:
        try:
            wallet_id = int(wallet_id)
        except ValueError:
            wallet_id = None

    if category_id:
        try:
            category_id = int(category_id)
        except ValueError:
            category_id = None

    # суммы
    amount_min = None
    if amount_min_str:
        try:
            amount_min = float(amount_min_str)
        except ValueError:
            pass

    amount_max = None
    if amount_max_str:
        try:
            amount_max = float(amount_max_str)
        except ValueError:
            pass

    # 4. Вызываем нашу сервисную функцию
    transactions_qs = get_filtered_transactions(
        period=period,
        start_date=s_date,
        end_date=e_date,
        exact_date=exact_date,
        transaction_type=transaction_type,
        wallet_id=wallet_id,
        category_id=category_id,
        amount_min=amount_min,
        amount_max=amount_max,
        description_substring=desc_substr
    )

    # 5. Передаём результат в шаблон. Кроме транзакций,
    #    передаём wallets и categories, чтобы отобразить выпадающие списки.
    context = {
        'transactions': transactions_qs,
        'wallets': wallets,
        'categories': categories,
    }
    return render(request, 'cashflow/transactions_list.html', context)

def wallet_balances_view(request):
    # Получаем список кошельков и их балансы (метод из services.py)
    data = get_wallet_balances()
    # Формируем контекст для шаблона
    context = {
        'wallets': data,
    }
    return render(request, 'cashflow/wallet_balances.html', context)

def monthly_report_view(request):
    # Пример: берём год из GET-параметра (или из текущего)
    year = request.GET.get('year', '2025')
    data = get_monthly_in_out(year=int(year))

    context = {
        'year': year,
        'months': data,
    }
    return render(request, 'cashflow/monthly_report.html', context)


def dashboard_view(request):
    """
    Основная «дашборд»-вьюха.
    Получает:
      - Год из GET (опционально),
      - Старые отчёты (cashflow_data, wallet_data, monthly_category_data),
      - Новый pivot-отчёт за последние 12 месяцев (pivot_12_data).
    Формирует «headers», чтобы в шаблоне красиво отобразить «Месяц Год».
    """
    # Опциональный фильтр по году
    year_param = request.GET.get('year')
    if year_param:
        year_param = int(year_param)
    else:
        year_param = None

    # 1. Сводка по видам деятельности (старый отчёт)
    cashflow_data = get_cashflow_summary_by_activity(year=year_param)

    # 2. Сводка по кошелькам
    wallet_data = get_wallet_balances()

    # 3. Сводка по статьям (категориям) — если ещё нужна
    monthly_category_data = get_monthly_cashflow_by_category(year=year_param)

    # 4. «Pivot»-отчёт за последние 12 месяцев (текущий + 11 предыдущих)
    pivot_12_data = get_activity_category_month_report_12()
    #    В нём ожидаем структуру:
    #    pivot_12_data = {
    #       "data": [...],
    #       "periods": [(2024,2), (2024,3), ..., (2025,1)]
    #    }

    # Итоговый контекст
    context = {
        'cashflow_data': cashflow_data,
        'wallet_data': wallet_data,
        'monthly_category_data': monthly_category_data,
        # 'months_list': months_list,  # <- если не используете, можно убрать
        'pivot_12_data': pivot_12_data,
        # 'headers': headers,  # <-- передаём заголовки для таблицы
    }
    return render(request, 'cashflow/dashboard.html', context)


def _add_months(base_date, months):
    """
    Утилита: прибавляет (или вычитает) из base_date заданное число месяцев.
    При отрицательном months = -x уходит x месяцев назад.
    """
    year = base_date.year
    month = base_date.month + months  # может стать < 1 или > 12
    # нормализуем год и месяц
    while month < 1:
        month += 12
        year -= 1
    while month > 12:
        month -= 12
        year += 1
    day = min(base_date.day, 28)  # чтобы не ошибиться с "31 февраля"
    return datetime.date(year, month, day)