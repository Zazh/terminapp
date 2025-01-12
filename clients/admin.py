from django.contrib import admin
from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("first_name", "primary_phone", "backup_phone", "company", "email")
    search_fields = ("first_name", "primary_phone", "email", "company")
    list_filter = ("company",)
    ordering = ("first_name",)
    fieldsets = (
        ("Основная информация", {
            "fields": ("first_name", "primary_phone", "backup_phone")
        }),
        ("Дополнительная информация", {
            "fields": ("company", "email"),
            "classes": ("collapse",),
        }),
    )

    def save_model(self, request, obj, form, change):
        print(f"Сохранение объекта: {obj}")
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        print(f"Удаление объекта: {obj}")
        super().delete_model(request, obj)

    def get_queryset(self, request):
        print("Получение списка объектов")
        queryset = super().get_queryset(request)
        return queryset
