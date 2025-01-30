# hr/admin.py

from django.contrib import admin
from .models import Department, Role, Employee, EmployeeInfo

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'department')
    list_filter = ('department',)
    search_fields = ('name', 'department__name')
    filter_horizontal = ('groups',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'status')
    list_filter = ('role__department', 'status')
    search_fields = ('user__username', 'user__email', 'role__name')


@admin.register(EmployeeInfo)
class EmployeeInfoAdmin(admin.ModelAdmin):
    list_display = ('employee', 'phone', 'hire_date')
    search_fields = ('employee__user__username', 'employee__user__email', 'phone')
