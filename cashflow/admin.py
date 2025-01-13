# cashflow/admin.py
from django.contrib import admin
from .models import Wallet, Category, Transaction, ActivityType


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')

@admin.register(ActivityType)
class ActivityTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'operation_type', 'description')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_type_display', 'amount', 'category', 'wallet', 'date')
    list_filter = ('category', 'wallet', 'date')
    search_fields = ('description',)

    def transaction_type_display(self, obj):
        """
        Отображает читабельный тип транзакции (Доход/Расход).
        """
        return obj.transaction_type

    transaction_type_display.short_description = "Тип транзакции"
