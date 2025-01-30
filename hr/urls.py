# hr/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from hr.api import (
    DepartmentViewSet,
    RoleViewSet,
    EmployeeViewSet,
    EmployeeInfoViewSet
)

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'employees-info', EmployeeInfoViewSet, basename='employee-info')

urlpatterns = [
    path('', include(router.urls)),
]
