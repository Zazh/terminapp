# cashflow/api.py
from rest_framework import viewsets, filters, permissions
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Prefetch
from .models import Transaction, Wallet, Category, ActivityType
from .serializers import (
    TransactionSerializer,
    WalletSerializer,
    CategorySerializer,
    ActivityTypeSerializer
)

class BaseViewSet(viewsets.ModelViewSet):
    """Базовый ViewSet с общими настройками"""
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = None  # Можно подключить PageNumberPagination

class TransactionViewSet(BaseViewSet):
    serializer_class = TransactionSerializer
    filterset_fields = {
        'amount': ['gte', 'lte'],
        'date': ['gte', 'lte', 'exact'],
        'category': ['exact'],
        'wallet': ['exact']
    }
    search_fields = ['description']
    ordering_fields = ['date', 'amount']

    # Явно указываем базовый queryset
    queryset = Transaction.objects.none()  # Заглушка

    def get_queryset(self):
        """Оптимизированный queryset с префетчингом"""
        return Transaction.objects.select_related(
            'category', 
            'wallet'
        ).prefetch_related(
            Prefetch('category__activity_type')
        ).order_by('-date')

class WalletViewSet(BaseViewSet):
    serializer_class = WalletSerializer
    search_fields = ['name']
    ordering_fields = ['name', 'balance']

    def get_queryset(self):
        return Wallet.objects.annotate_balance().order_by('-balance')

    # Добавьте явный queryset для совместимости
    queryset = Wallet.objects.all()

class CategoryViewSet(BaseViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.select_related('activity_type')
    filterset_fields = ['operation_type', 'activity_type']
    search_fields = ['name']

class ActivityTypeViewSet(BaseViewSet):
    serializer_class = ActivityTypeSerializer
    queryset = ActivityType.objects.prefetch_related('categories')
    search_fields = ['name']
