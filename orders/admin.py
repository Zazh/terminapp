from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import OrderItem


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'quantity', 'price', 'wallet', 'status')
    list_filter = ('status', 'wallet')
    search_fields = ('product__name',)
    readonly_fields = ['price']

    def save_model(self, request, obj, form, change):
        """
        Проверяем, чтобы статус был корректным при сохранении.
        """
        if obj.status == 'refunded' and obj.status != 'completed':
            raise ValidationError("Возврат возможен только для завершённых заказов.")
        super().save_model(request, obj, form, change)
