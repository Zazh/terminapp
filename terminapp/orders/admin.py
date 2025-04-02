# orders/admin.py
from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import Order, OrderItem, OrderItemRefund
from .services import recalc_order_total

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('product', 'quantity', 'discount', 'status', 'wallet')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'client')
    search_fields = ('client__first_name', 'client__primary_phone')
    readonly_fields = ('total_amount', 'created_at', 'updated_at')
    inlines = [OrderItemInline]

    def save_model(self, request, obj, form, change):
        """
        Сохраняем сам заказ.
        """
        # Важно: сейчас у obj (Order) уже может быть pk, если это редактирование,
        # или не быть, если это новый заказ. Но мы здесь не пересчитываем сумму.
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        """
        Сохраняем инлайны (OrderItem), а потом вызываем сервисный пересчёт.
        """
        # 1) Сохраняем все OrderItem
        instances = formset.save()
        # 2) Теперь у заказа (form.instance) есть pk, и все OrderItem сохранены.
        order = form.instance
        # 3) Вызываем нашу сервисную функцию для пересчёта
        recalc_order_total(order)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Админ-представление для позиций заказа (OrderItem).
    """
    list_display = ('id', 'product', 'quantity', 'price', 'discount', 'wallet', 'status')
    list_filter = ('status', 'wallet')
    search_fields = ('product__name',)
    readonly_fields = ['price']
    fields = ('product', 'quantity', 'discount', 'wallet', 'status')

    def save_model(self, request, obj, form, change):
        """
        Пример кастомной логики при сохранении.
        Учитывайте фактические статусы в STATUS_CHOICES:
        ('pending', 'Оплачен', 'cancelled', 'deleted').
        """
        # Если вам нужно проверить какие-то особые статусы, делайте это здесь.
        # Пример: Если кто-то выставит статус 'refunded' напрямую (не предусмотрен),
        # мы можем выбросить ошибку.
        if obj.status == 'refunded':
            raise ValidationError("Статус 'refunded' не используется. Создайте возврат через OrderItemRefund.")
        super().save_model(request, obj, form, change)


@admin.register(OrderItemRefund)
class OrderItemRefundAdmin(admin.ModelAdmin):
    """
    Админ-представление для возвратов (OrderItemRefund).
    Отдельная сущность, позволяющая независимо управлять возвратами.
    """
    list_display = (
        'id',
        'order_item',
        'refund_date',
        'refund_quantity',
        'refund_amount',
        'wallet',
    )
    list_filter = ('refund_date', 'wallet')
    search_fields = ('reason', 'order_item__product__name',)
    fields = (
        'order_item',
        'refund_quantity',
        'refund_amount',
        'wallet',
        'reason',
        'refund_date',
    )
    readonly_fields = ('refund_date',)

    def save_model(self, request, obj, form, change):
        """
        Если нужно выполнить дополнительные действия после сохранения (например,
        пересчитать сумму заказа), можно сделать это здесь.
        """
        super().save_model(request, obj, form, change)
        # Пример логики пересчёта суммы заказа (при наличии соответствующей функции):
        # order = obj.order_item.order
        # recalc_order_total(order)