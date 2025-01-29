# analytics/api.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .models import Report
from .services import get_cashflow_data, get_wallet_data
from .serializers import (
    ReportSerializer,
    CashflowAnalysisSerializer,
    CashflowTotalSerializer,
    WalletBalanceSerializer
)


class BaseViewSet(viewsets.GenericViewSet):
    """Базовый ViewSet с общими настройками"""
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    @method_decorator(cache_page(60 * 5))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ReportViewSet(BaseViewSet, viewsets.ModelViewSet):
    """CRUD для аналитических отчетов"""
    serializer_class = ReportSerializer
    filterset_fields = ['created_at', 'updated_at']
    ordering_fields = ['-created_at']

    # Явно указываем базовый queryset
    queryset = Report.objects.none()  # Заглушка



class AnalyticsViewSet(BaseViewSet):
    """Аналитические данные с кэшированием"""

    permission_classes = [permissions.IsAuthenticated]

    queryset = []  # Фиктивный queryset
    filter_backends = []  # Отключаем фильтры для этого ViewSet
    pagination_class = None
    # Убираем декоратор кэширования для list (метод не используется)
    def list(self, request, *args, **kwargs):
        return Response(
            {"detail": "Используйте кастомные экшен: /wallet_balances/ или /cashflow/"},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'], url_path='wallet_balances')
    def get_wallet_balances(self, request):
        """Балансы кошельков"""
        try:
            balances = get_wallet_data()
            serializer = WalletBalanceSerializer(balances, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def cashflow(self, request):
        """Анализ денежных потоков"""
        try:
            data = get_cashflow_data()
            details_serializer = CashflowAnalysisSerializer(data['details'], many=True)
            total_serializer = CashflowTotalSerializer(data['total'])
            return Response({
                "details": details_serializer.data,
                "total": total_serializer.data
            })
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )