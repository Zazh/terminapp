# companys/admin.py

from django.contrib import admin
from .models import Company

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """
    Админка для управления компаниями (Tenants).
    """
    list_display = ('name', 'subdomain', 'billing_plan', 'created_at')
    search_fields = ('name', 'subdomain')
    list_filter = ('billing_plan', 'created_at')
