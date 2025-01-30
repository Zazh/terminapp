# hr/api.py

from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import (
    Department,
    Role,
    Employee,
    EmployeeInfo
)
from .serializers import (
    DepartmentSerializer,
    RoleSerializer,
    EmployeeSerializer,
    EmployeeInfoSerializer
)

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['name', 'code']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code']


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.select_related('department').prefetch_related('groups').all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['name', 'department__name']
    search_fields = ['name', 'department__name']
    ordering_fields = ['name']


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related('user', 'role__department').all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role__name', 'role__department__name', 'status']
    search_fields = ['user__username', 'user__email', 'role__name']
    ordering_fields = ['user__username', 'status']


class EmployeeInfoViewSet(viewsets.ModelViewSet):
    queryset = EmployeeInfo.objects.select_related('employee__user', 'employee__role').all()
    serializer_class = EmployeeInfoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['employee__status',]
    search_fields = ['phone', 'employee__user__email']
    ordering_fields = ['hire_date', 'phone']
