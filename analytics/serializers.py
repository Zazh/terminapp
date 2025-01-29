# analytics/serializers.py
from rest_framework import serializers
from .models import Report

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class CashflowAnalysisSerializer(serializers.Serializer):
    activity_type = serializers.CharField(
        allow_null=True,
        default='Без вида деятельности'
    )
    income = serializers.DecimalField(max_digits=12, decimal_places=2)
    expense = serializers.DecimalField(max_digits=12, decimal_places=2)
    net_flow = serializers.DecimalField(max_digits=12, decimal_places=2)

class CashflowTotalSerializer(serializers.Serializer):
    income = serializers.DecimalField(max_digits=12, decimal_places=2)
    expense = serializers.DecimalField(max_digits=12, decimal_places=2)
    net_flow = serializers.DecimalField(max_digits=12, decimal_places=2)

class WalletBalanceSerializer(serializers.Serializer):
    wallet__name = serializers.CharField()
    balance = serializers.DecimalField(max_digits=10, decimal_places=2)