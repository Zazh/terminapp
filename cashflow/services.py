# cashflow/services.py

from django.db.models import Sum, Case, When, F, DecimalField, Value, Q
from django.db.models.functions import ExtractMonth, Coalesce
from .models import Transaction
from datetime import date, timedelta, datetime

def get_filtered_transactions(
    period=None,
    start_date=None,
    end_date=None,
    exact_date=None,
    transaction_type=None,
    wallet_id=None,  # <-- ОБЯЗАТЕЛЬНО ДОЛЖНО БЫТЬ
    category_id=None,
    amount_min=None,
    amount_max=None,
    description_substring=None
):
    """
    Фильтрует QuerySet Transaction на основании заданных параметров.
    Варианты:
    - period         (str) : 'today', 'yesterday', 'last_7_days', ... 'all_time', 'custom'
    - start_date     (date): начало периода (для 'custom')
    - end_date       (date): конец периода (для 'custom')
    - exact_date     (date): конкретная дата, имеет приоритет над period
    - transaction_type (str): 'income', 'expense', 'transfer' (если используется)
    - wallet_id      (int)
    - category_id    (int)
    - amount_min     (Decimal|float)
    - amount_max     (Decimal|float)
    - description_substring (str)
    """
    qs = Transaction.objects.select_related('category', 'wallet').all()

    # 1. Обработка exact_date
    if exact_date:
        qs = qs.filter(date=exact_date)
    else:
        # 2. Если exact_date не задан, проверяем period
        if period:
            from .services import get_date_range_for_period
            d_start, d_end = get_date_range_for_period(period, start_date, end_date)
            if d_start and d_end:
                qs = qs.filter(date__range=[d_start, d_end])
            elif d_start:
                qs = qs.filter(date__gte=d_start)
            elif d_end:
                qs = qs.filter(date__lte=d_end)
            else:
                # all_time (или не распознано) -> не фильтруем
                pass

    # 3. Фильтр по типу операции
    #    transaction_type у вас в модели — это property, которое возвращает 'income'/'expense'.
    #    Но для фильтрации нам нужно смотреть на group.name
    if transaction_type == 'income':
        qs = qs.filter(category__group__name='Поступление')
    elif transaction_type == 'expense':
        qs = qs.filter(category__group__name='Выбытие')
    elif transaction_type == 'transfer':
        qs = qs.filter(category__group__name='Перевод')  # если вы добавите такую группу

    # 4. Кошелёк
    if wallet_id:
        qs = qs.filter(wallet_id=wallet_id)

    # 5. Категория
    if category_id:
        qs = qs.filter(category_id=category_id)

    # 6. Сумма
    if amount_min is not None:
        qs = qs.filter(amount__gte=amount_min)
    if amount_max is not None:
        qs = qs.filter(amount__lte=amount_max)

    # 7. Описание (substring)
    if description_substring:
        qs = qs.filter(description__icontains=description_substring)

    # Сортируем по дате (новые сверху)
    qs = qs.order_by('-date', '-id')

    return qs

def get_date_range_for_period(period: str, custom_start=None, custom_end=None):
    """
    Упрощённая версия функции, возвращает кортеж (start_date, end_date)
    на основании заданного периода. Для 'custom' используется custom_start и custom_end.

    Если period не распознано или period='all_time', возвращаем (None, None).
    """
    today = date.today()

    if period == 'today':
        return (today, today)
    elif period == 'yesterday':
        y = today - timedelta(days=1)
        return (y, y)
    elif period == 'last_7_days':
        return (today - timedelta(days=7), today)
    elif period == 'last_30_days':
        return (today - timedelta(days=30), today)
    elif period == 'all_time':
        return (None, None)
    elif period == 'custom':
        # Используем то, что передал пользователь
        return (custom_start, custom_end)

    # Если ничего не подошло — считаем, что все время.
    return (None, None)

def get_wallet_balances():
    """
    Возвращает список словарей {wallet_id, wallet__name, balance}
    c текущим балансом по каждому кошельку.

    Предполагаем, что:
      - category.group.name == "Поступление" => Доход
      - category.group.name == "Выбытие" => Расход
    """
    qs = (
        Transaction.objects
        .values('wallet_id', 'wallet__name')
        .annotate(
            balance=Sum(
                Case(
                    When(category__group__name='Поступление', then=F('amount')),
                    When(category__group__name='Выбытие', then=-F('amount')),
                    output_field=DecimalField()
                )
            )
        )
    )
    return qs


def get_monthly_in_out(year: int):
    """
    Возвращает агрегаты поступлений/расходов по месяцам в заданном году.
    [
      {'month': 1, 'income': 1000, 'expense': 500},
      {'month': 2, 'income': 2000, 'expense': 750},
      ...
    ]
    Предполагаем тот же принцип: у транзакций, чья category.group.name == "Поступление" -> доход,
    "Выбытие" -> расход.
    """

    # Доходы (Поступление)
    incomes = (
        Transaction.objects
        .filter(category__group__name='Поступление', date__year=year)
        .annotate(month=ExtractMonth('date'))
        .values('month')
        .annotate(total_income=Sum('amount'))
    )

    # Расходы (Выбытие)
    expenses = (
        Transaction.objects
        .filter(category__group__name='Выбытие', date__year=year)
        .annotate(month=ExtractMonth('date'))
        .values('month')
        .annotate(total_expense=Sum('amount'))
    )

    # Объединяем данные incomes и expenses по каждому месяцу
    data = []
    for m in range(1, 13):
        inc = next((i['total_income'] for i in incomes if i['month'] == m), 0)
        exp = next((e['total_expense'] for e in expenses if e['month'] == m), 0)
        data.append({
            'month': m,
            'income': inc,
            'expense': exp,
        })
    return data


def get_cashflow_summary_by_activity(year: int = None):
    """
    Возвращает список словарей с суммами доходов/расходов и итоговым потоком
    (net_flow) в разрезе видов деятельности (ActivityType).

    Параметр year не обязателен: если его передать, данные будут фильтроваться
    по году в поле date. Если year=None, берутся все данные.
    """
    qs = Transaction.objects.all()

    if year:
        qs = qs.filter(date__year=year)

    # Группировка по названию вида деятельности
    qs_annotated = (
        qs
        .values(activity_type=F('category__activity_type__name'))
        .annotate(
            income=Coalesce(
                Sum(
                    Case(
                        When(category__group__name='Поступление', then=F('amount')),
                        output_field=DecimalField()
                    )
                ),
                Value(0, output_field=DecimalField())
            ),
            expense=Coalesce(
                Sum(
                    Case(
                        When(category__group__name='Выбытие', then=F('amount')),
                        output_field=DecimalField()
                    )
                ),
                Value(0, output_field=DecimalField())
            )
        )
    )

    # Формируем финальный список
    results = []
    total_income = 0
    total_expense = 0

    for row in qs_annotated:
        activity_type_name = row['activity_type'] or "Без вида деятельности"
        income = row['income']
        expense = row['expense']
        net_flow = income - expense

        total_income += income
        total_expense += expense

        results.append({
            "activity_type": activity_type_name,
            "income": income,
            "expense": expense,
            "net_flow": net_flow
        })

    # Общий итог по всем ActivityType
    total_data = {
        "activity_type": "Итого по всем видам",
        "income": total_income,
        "expense": total_expense,
        "net_flow": total_income - total_expense
    }

    return {
        "details": results,
        "total": total_data
    }


def get_cashflow_summary_by_category(year: int = None):
    """
    Возвращает список словарей с суммами доходов/расходов и итоговым потоком
    (net_flow) в разрезе категорий (Category).

    Параметр year не обязателен:
      - Если year != None, фильтруем транзакции по date__year=year
      - Если year=None, берём все транзакции
    """
    qs = Transaction.objects.all()

    if year:
        qs = qs.filter(date__year=year)

    qs_annotated = (
        qs
        .values(category_name=F('category__name'))  # Группируем по названию категории
        .annotate(
            income=Coalesce(
                Sum(
                    Case(
                        When(category__group__name='Поступление', then=F('amount')),
                        output_field=DecimalField()
                    )
                ),
                Value(0, output_field=DecimalField())
            ),
            expense=Coalesce(
                Sum(
                    Case(
                        When(category__group__name='Выбытие', then=F('amount')),
                        output_field=DecimalField()
                    )
                ),
                Value(0, output_field=DecimalField())
            )
        )
    )

    # Формируем структуру выходных данных
    results = []
    total_income = 0
    total_expense = 0

    for row in qs_annotated:
        cat_name = row['category_name'] or "Без категории"
        inc = row['income']
        exp = row['expense']
        net_flow = inc - exp

        # Накапливаем общие итоги
        total_income += inc
        total_expense += exp

        results.append({
            "category": cat_name,
            "income": inc,
            "expense": exp,
            "net_flow": net_flow
        })

    # "Итого" строка по всем категориям
    total_data = {
        "category": "Итого по всем статьям",
        "income": total_income,
        "expense": total_expense,
        "net_flow": total_income - total_expense
    }

    return {
        "details": results,
        "total": total_data
    }


def get_all_transactions(year: int = None):
    """
    Возвращает все транзакции (операции).
    Если year != None, то фильтруем их по дате (date__year=year).
    Сортируем по дате (убывание), чтобы последние были вверху.
    """
    qs = Transaction.objects.select_related('category', 'wallet').order_by('-date')

    if year:
        qs = qs.filter(date__year=year)

    return qs