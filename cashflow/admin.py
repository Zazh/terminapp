# finance/admin.py

from django.contrib import admin
from .models import Category, Group, Transaction, BusinessDirection, ActivityType, Wallet

@admin.register(BusinessDirection)
class BusinessDirectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(ActivityType)
class ActivityTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'group', 'activity_type')
    list_filter = ('group', 'activity_type')
    search_fields = ('name', 'description')

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name', )

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'amount', 'category', 'wallet', 'date', 'transaction_type_display')

    @admin.display(description="Тип транзакции")
    def transaction_type_display(self, obj):
        return obj.get_transaction_type_display()