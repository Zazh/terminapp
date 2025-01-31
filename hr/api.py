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

class CompanyFilterMixin:
    """
    Пример: автоматическая фильтрация по `company`
    (используя некое поле request.user.current_company).
    Вы можете адаптировать логику получения текущей компании
    под свои нужды (сабдомен, параметр, выбранная компания и т.д.)
    """

    def get_queryset(self):
        qs = super().get_queryset()
        # Если user.is_superuser: вернуть все
        if self.request.user.is_superuser:
            return qs
        # Иначе фильтруем
        company = getattr(self.request.user, 'current_company', None)
        if company is not None:
            return qs.filter(company=company)
        return qs.none()


class DepartmentViewSet(CompanyFilterMixin, viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['name', 'code']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code']


class RoleViewSet(CompanyFilterMixin, viewsets.ModelViewSet):
    queryset = Role.objects.select_related('department').prefetch_related('groups').all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['name', 'department__name']
    search_fields = ['name', 'department__name']
    ordering_fields = ['name']


class EmployeeViewSet(CompanyFilterMixin, viewsets.ModelViewSet):
    # Вместо select_related('role__department') используем prefetch_related('roles__department'),
    # т.к. roles - это M2M, а department - ForeignKey внутри Role.
    queryset = Employee.objects.select_related('company', 'user').prefetch_related('roles__department').all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # Теперь фильтруем по множественным ролям:
    # roles__name вместо role__name
    # roles__department__name вместо role__department__name
    filterset_fields = ['roles__name', 'roles__department__name', 'status']
    search_fields = ['user__username', 'user__email', 'roles__name']
    ordering_fields = ['user__username', 'status']


class EmployeeInfoViewSet(CompanyFilterMixin, viewsets.ModelViewSet):
    """
    Можно тоже наследовать CompanyFilterMixin,
    но т.к. вы уже определили свою get_queryset,
    можно оставить явную фильтрацию через employee__company.
    Или же совмещаем их.
    """
    queryset = EmployeeInfo.objects.select_related('employee__user', 'employee__company')
    serializer_class = EmployeeInfoSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['employee__status']
    search_fields = ['phone', 'employee__user__email']
    ordering_fields = ['hire_date', 'phone']

