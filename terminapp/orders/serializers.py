# serializers.py
from rest_framework import serializers
from .models import Order, OrderItem, OrderItemRefund

class OrderItemSerializer(serializers.ModelSerializer):
    # Если хотим отображать название продукта
    product_name = serializers.ReadOnlyField(source='product.name')
    # Если нужно отобразить сумму позиции
    line_amount = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'order',
            'product',
            'product_name',
            'quantity',
            'price',
            'discount',
            'wallet',
            'status',
            'line_amount',
        ]

    def get_line_amount(self, obj: OrderItem):
        return obj.calculate_amount()

class OrderSerializer(serializers.ModelSerializer):
    # Если хотим выводить сразу список позиций
    order_items = OrderItemSerializer(many=True, read_only=True)
    # Или можно сделать nested create, но это отдельная история

    class Meta:
        model = Order
        fields = [
            'id',
            'client',
            'status',
            'total_amount',
            'created_at',
            'updated_at',
            'order_items',
        ]
        read_only_fields = ['total_amount', 'created_at', 'updated_at']


class OrderItemRefundSerializer(serializers.ModelSerializer):
    """
    Сериализатор для возврата позиции заказа.
    """
    class Meta:
        model = OrderItemRefund
        fields = [
            'id',
            'order_item',
            'refund_date',
            'reason',
            'refund_quantity',
            'refund_amount',
            'wallet'
        ]
        # Поле refund_date установлено auto_now_add=True,
        # поэтому логично сделать его только для чтения
        read_only_fields = ['refund_date']