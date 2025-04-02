# hr/admin.py

from django.contrib import admin
from .models import Department, Role, Employee, EmployeeInfo, Company

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """
    Админка для управления компаниями (Tenants).
    """
    list_display = ('name', 'subdomain', 'billing_plan', 'created_at')
    search_fields = ('name', 'subdomain')
    list_filter = ('billing_plan', 'created_at')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'company')
    list_filter = ('company',)
    search_fields = ('name', 'company__name')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'department')
    list_filter = ('company', 'department')
    search_fields = ('name', 'company__name', 'department__name')
    filter_horizontal = ('groups',)  # Если Role.groups связаны с Django Groups


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'status')
    list_filter = ('company', 'status')
    search_fields = ('user__username', 'user__email', 'company__name')
    filter_horizontal = ('roles',)  # M2M-field для ролей


@admin.register(EmployeeInfo)
class EmployeeInfoAdmin(admin.ModelAdmin):
    list_display = ('employee', 'phone', 'hire_date')
    search_fields = ('employee__user__username', 'employee__user__email', 'phone')
