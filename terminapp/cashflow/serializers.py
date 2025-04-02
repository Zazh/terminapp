# cashflow/serializers.py
from rest_framework import serializers
from .models import Transaction, Wallet, Category, ActivityType


class WalletSerializer(serializers.ModelSerializer):
    balance = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Wallet
        fields = ['id', 'name', 'created_at', 'updated_at', 'balance']
        # company не выводим наружу или делаем поле read_only,
        # т.к. оно ставится автоматически


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        # при необходимости исключите или сделайте поля read_only,
        # если не хотите, чтобы Category меняли через API.


class ActivityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityType
        fields = '__all__'
        # аналогично выше


class TransactionSerializer(serializers.ModelSerializer):
    """
    Для CRUD по Transaction.
    """
    transaction_type = serializers.ReadOnlyField()

    class Meta:
        model = Transaction
        fields = [
            'id', 'wallet', 'category', 'amount', 'description', 'date',
            'transaction_type', 'content_type', 'object_id'
        ]
        # company не выводим / либо делаем read_only