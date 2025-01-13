# orders/admin.py

from django.contrib import admin
from .models import Order, OrderItem
from cashflow.models import Transaction


class OrderItemInline(admin.TabularInline):
    """
    Inline для редактирования элементов заказа.
    """
    model = OrderItem
    extra = 1
    readonly_fields = ['price']  # Поле "Цена" доступно только для чтения

    def save_model(self, request, obj, form, change):
        """
        Устанавливает цену из связанного продукта, если она не задана.
        """
        if not obj.price:
            obj.price = obj.product.price
        super().save_model(request, obj, form, change)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'order_date', 'total_amount', 'status')
    list_filter = ('status', 'order_date')
    search_fields = ('customer__first_name', 'customer__last_name', 'id')
    inlines = [OrderItemInline]
    readonly_fields = ('total_amount',)  # Поле только для чтения

    def save_model(self, request, obj, form, change):
        """
        Автоматический пересчёт суммы заказа при сохранении.
        """
        obj.save()  # Метод save() модели уже пересчитает сумму
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        """
        Оптимизируем запросы в админке, используя select_related.
        """
        qs = super().get_queryset(request)
        return qs.select_related('customer')  # Загружаем данные клиента вместе с заказом


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Админка для модели OrderItem (опционально, если редактирование необходимо).
    """
    list_display = ('id', 'order', 'product', 'quantity', 'price', 'wallet', 'status')
    list_filter = ('status', 'wallet')
    search_fields = ('product__name', 'order__id')
    readonly_fields = ['price']  # Поле "Цена" доступно только для чтения

    def save_model(self, request, obj, form, change):
        # Проверяем возможность перехода на "refund"
        if obj.status == 'refund':
            original_status = OrderItem.objects.get(pk=obj.pk).status if obj.pk else None
            if original_status != 'completed':
                raise ValueError("Возврат средств возможен только для завершенных заказов.")
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        """
        Оптимизируем запросы в админке для элементов заказа.
        """
        qs = super().get_queryset(request)
        return qs.select_related('product', 'order', 'wallet')
