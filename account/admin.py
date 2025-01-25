from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from django.utils.translation import gettext_lazy as _

class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("email", "phone_number")}),
        (_("Permissions"), {"fields": ("is_active", "is_client", "is_staff", "is_superuser")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    readonly_fields = ("date_joined",)
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "phone_number", "password1", "password2",
                       "is_client", "is_staff", "is_superuser"),
        }),
    )
    list_display = ("username", "email", "phone_number", "is_staff", "is_superuser", "is_client", "date_joined")
    search_fields = ("username", "email", "phone_number")
    ordering = ("username",)

admin.site.register(User, UserAdmin)