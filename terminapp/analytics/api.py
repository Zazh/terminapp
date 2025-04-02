# analytics/api.py
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend, DateFromToRangeFilter
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from cashflow.models import Transaction  # Добавлен импорт модели
from .models import Report
from .services import get_cashflow_data, get_wallet_data
from .serializers import (
    ReportSerializer,
    CashflowAnalysisSerializer,
    CashflowTotalSerializer,
    WalletBalanceSerializer
)
import django_filters


class ReportFilter(django_filters.FilterSet):
    created_at = DateFromToRangeFilter()
    updated_at = DateFromToRangeFilter()

    class Meta:
        model = Report
        fields = ['name']


class BaseViewSet(viewsets.GenericViewSet):
    """Базовый ViewSet с общими настройками"""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    pagination_class = None

    @method_decorator(cache_page(60 * 5))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ReportViewSet(BaseViewSet, viewsets.ModelViewSet):
    """CRUD для аналитических отчетов"""
    serializer_class = ReportSerializer
    filterset_class = ReportFilter
    search_fields = ['name', 'data']
    ordering_fields = ['created_at', 'updated_at', 'name']
    queryset = Report.objects.all()

    def get_queryset(self):
        return super().get_queryset().filter(
            user=self.request.user
        ).select_related('user')


class AnalyticsFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(
        field_name='date',
        lookup_expr='gte',
        label="Дата от (ГГГГ-ММ-ДД)"
    )
    end_date = django_filters.DateFilter(
        field_name='date',
        lookup_expr='lte',
        label="Дата до (ГГГГ-ММ-ДД)"
    )
    wallet = django_filters.NumberFilter(
        field_name='wallet_id',
        label="ID кошелька"
    )
    category_type = django_filters.CharFilter(
        field_name='category__activity_type__name',
        label="Тип активности"
    )

    class Meta:
        model = Transaction  # Указываем базовую модель
        fields = ['start_date', 'end_date', 'wallet', 'category_type']


class AnalyticsViewSet(BaseViewSet):
    """Аналитические данные с фильтрацией в UI"""
    filterset_class = AnalyticsFilter
    filter_backends = [DjangoFilterBackend]
    queryset = Transaction.objects.none()

    def list(self, request, *args, **kwargs):
        """Заглушка для базового URL"""
        return Response(
            {
                "detail": "Используйте кастомные экшены:",
                "available_endpoints": {
                    "wallet_balances": "/wallet_balances/",
                    "cashflow": "/cashflow/"
                }
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'], url_path='wallet_balances')
    def get_wallet_balances(self, request):
        """Балансы кошельков с фильтрацией"""
        filters = self.filterset_class(request.GET, queryset=self.queryset).data
        balances = get_wallet_data(**filters)
        serializer = WalletBalanceSerializer(balances, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def cashflow(self, request):
        """Анализ денежных потоков с фильтрацией"""
        filters = self.filterset_class(request.GET, queryset=self.queryset).data
        data = get_cashflow_data(**filters)
        return Response({
            "details": CashflowAnalysisSerializer(data['details'], many=True).data,
            "total": CashflowTotalSerializer(data['total']).data
        })