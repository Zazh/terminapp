# finance/admin.py

from django.contrib import admin
from .models import Category, Transaction, BusinessDirection, ActivityType, Wallet

@admin.register(BusinessDirection)
class BusinessDirectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(ActivityType)
class ActivityTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'operation_type', 'activity_type')  # Добавлено 'activity_type'
    list_filter = ('operation_type', 'activity_type')  # Добавлено 'activity_type' в фильтры
    search_fields = ('name', 'description')  # Поиск по названию и описанию


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'updated_at')
    search_fields = ('name', )

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'amount', 'category', 'wallet', 'date', 'transaction_type_display')

    @admin.display(description="Тип транзакции")
    def transaction_type_display(self, obj):
        return obj.get_transaction_type_display()