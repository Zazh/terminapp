# orders/forms.py
from django import forms
from .models import Order, OrderItem, OrderItemRefund
from clients.models import Client

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        # total_amount пересчитывается автоматически — обычно не даём редактировать вручную
        # status устанавливается по умолчанию в 'pending', либо вы можете его не показывать.
        # Если нужно, добавьте 'status' или сделайте отдельный выбор.
        fields = ['client']  # пример: выбираем только клиента, статус по умолчанию "pending"

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        # Обычно пользователь вводит только product, quantity, discount, wallet (если нужно).
        # Поле price берётся из продукта, если явно не указали.
        # status пусть по умолчанию = 'pending'.
        fields = ['product', 'quantity', 'discount', 'wallet']
        # Если хотите показывать и price, можно добавить сюда 'price'.
        # Но тогда следите за тем, что price при отсутствии — копируется из product.

class OrderItemRefundForm(forms.ModelForm):
    """
    Форма для возврата позиций заказа.
    """
    class Meta:
        model = OrderItemRefund
        fields = ['refund_quantity', 'refund_amount', 'reason', 'wallet']

    def clean_refund_quantity(self):
        refund_quantity = self.cleaned_data['refund_quantity']
        if refund_quantity <= 0:
            raise forms.ValidationError("Количество к возврату должно быть больше 0.")
        return refund_quantity


class RefundSearchForm(forms.Form):
    """
    Форма для поиска клиента по основному номеру телефона.
    """
    phone = forms.CharField(
        required=True,
        label="Основной телефон клиента",
        max_length=20,
        help_text="Введите основной номер телефона клиента"
    )

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()
        if not phone:
            raise forms.ValidationError("Номер телефона обязателен.")
        return phone