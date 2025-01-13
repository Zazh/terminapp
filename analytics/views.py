# analytics/views.py
from django.shortcuts import render
from .services import get_cashflow_data, get_monthly_category_data, get_pivot_12_data, get_wallet_data, get_all_transactions


def dashboard(request):
    """
    Отображение аналитического дашборда.
    """
    context = {
        'cashflow_data': get_cashflow_data(),
        'monthly_category_data': get_monthly_category_data(),
        'pivot_12_data': get_pivot_12_data(),
        'wallet_data': get_wallet_data(),
    }
    return render(request, 'analytics/dashboard.html', context)

def transaction_report(request):
    """
    Отображение отчёта о всех транзакциях.
    """
    transactions, total_sum = get_all_transactions()
    context = {
        'transactions': transactions,
        'total_sum': total_sum,
    }
    return render(request, 'analytics/transaction_report.html', context)
