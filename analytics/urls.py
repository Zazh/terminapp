# analytics/urls.py
from django.urls import path
from .views import dashboard, transaction_report

urlpatterns = [
    path('dashboard/', dashboard, name='analytics_dashboard'),
    path('transaction-report/', transaction_report, name='transaction_report'),
]
