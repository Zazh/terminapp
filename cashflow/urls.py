from django.urls import path
from .views import (
    wallet_balances_view,
    monthly_report_view,
    dashboard_view,
    transactions_list_view,
)

urlpatterns = [
    path('wallets/', wallet_balances_view, name='wallet_balances'),
    path('monthly-report/', monthly_report_view, name='monthly_report'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('transactions/', transactions_list_view, name='transactions_list'),
]
