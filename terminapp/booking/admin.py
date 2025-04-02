from django.contrib import admin
from .models import Booking, BookingItem

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "client_name",
        "start_datetime",
        "end_datetime",
        "status",
        "created_at",
    )
    list_filter = ("status", "start_datetime", "end_datetime", "created_at")
    search_fields = ("order__id", "order__client__first_name", "order__client__primary_phone")

    def client_name(self, obj):
        if obj.client:
            return f"{obj.client.first_name} / {obj.client.primary_phone}"
        return "-"
    client_name.short_description = "Клиент"


@admin.register(BookingItem)
class BookingItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "booking",
        "order_item",
        "quantity",
        "status",
        "start_datetime",
        "end_datetime",
    )
    list_filter = ("status", "booking__status")
    search_fields = ("booking__id", "order_item__product__name", "booking__order__client__first_name")