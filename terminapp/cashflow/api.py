# cashflow/api.py

from rest_framework import viewsets, filters, permissions
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Transaction, Wallet, Category, ActivityType
from .serializers import (
    TransactionSerializer,
    WalletSerializer,
    CategorySerializer,
    ActivityTypeSerializer
)
# Импортируем функции из service.py
from .services import (
    create_wallet,
    create_transaction,
    get_wallets_for_company,
    parse_transaction_filters,
    get_filtered_transactions
)


class BaseViewSet(viewsets.ModelViewSet):
    """Базовый ViewSet с общими настройками."""
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    permission_classes = [permissions.IsAuthenticated]  # или IsAuthenticatedOrReadOnly
    pagination_class = None  # Можно подключить PageNumberPagination


class WalletViewSet(BaseViewSet):
    serializer_class = WalletSerializer
    search_fields = ['name']
    ordering_fields = ['name', 'balance']

    def get_queryset(self):
        """
        Возвращаем только кошельки текущей компании,
        пользуясь сервисной функцией get_wallets_for_company.
        """
        company = getattr(self.request, 'current_company', None)
        if not company:
            return Wallet.objects.none()
        return get_wallets_for_company(company)

    def perform_create(self, serializer):
        """
        При создании кошелька вызываем сервис create_wallet(...).
        """
        company = getattr(self.request, 'current_company', None)
        if not company:
            raise ValueError("Невозможно создать кошелёк без текущей компании.")

        wallet = create_wallet(
            company=company,
            name=serializer.validated_data['name']
        )
        serializer.instance = wallet


class TransactionViewSet(BaseViewSet):
    """
    Здесь основные изменения:
    - Списки (list) строим через parse_transaction_filters() + get_filtered_transactions().
    - Остальные операции (create) через сервис create_transaction().
    """
    serializer_class = TransactionSerializer
    # Если вы хотите сохранить DjangoFilterBackend для простых фильтров
    # через ?amount__gte=... и т.п., оставьте filterset_fields
    filterset_fields = {
        'amount': ['gte', 'lte'],
        'date': ['gte', 'lte', 'exact'],
        'category': ['exact'],
        'wallet': ['exact']
    }
    search_fields = ['description']
    ordering_fields = ['date', 'amount']

    def get_queryset(self):
        """
        По умолчанию даём пустой QS, потому что реальная логика получения
        списка транзакций будет в методе list().
        """
        return Transaction.objects.none()

    def list(self, request, *args, **kwargs):
        """
        Переопределяем list(), чтобы использовать сервисный слой:
        1) Парсим фильтры
        2) Получаем QS и total_sum
        3) Применяем пагинацию (если нужно)
        4) Отдаём результат + total_sum
        """
        company = getattr(request, 'current_company', None)
        if not company:
            return Response({"detail": "Компания не определена."}, status=400)

        # Парсим GET-параметры (period, exact_date, start_date, и т.п.)
        filters = parse_transaction_filters(request)

        # Вызываем сервисный метод, передавая company и распаковывая filters
        queryset, total_sum = get_filtered_transactions(company=company, **filters)

        # Если хотите применить встроенную пагинацию DRF:
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'results': serializer.data,
                'total_sum': total_sum,
            })

        # Без пагинации — просто сериализуем все записи
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'total_sum': total_sum,
        })

    def perform_create(self, serializer):
        """
        Создаём транзакцию через сервис create_transaction(...).
        """
        company = getattr(self.request, 'current_company', None)
        if not company:
            raise ValueError("Невозможно создать транзакцию без текущей компании.")

        wallet = serializer.validated_data['wallet']
        category = serializer.validated_data['category']
        amount = serializer.validated_data['amount']
        description = serializer.validated_data.get('description', "")

        # Если есть content_type/object_id, можете извлечь их и передать reason_object
        reason_object = None  # Логика по установке reason_object, если нужно

        new_tx = create_transaction(
            company=company,
            wallet=wallet,
            category=category,
            amount=amount,
            description=description,
            reason_object=reason_object,
        )
        serializer.instance = new_tx


class CategoryViewSet(BaseViewSet):
    serializer_class = CategorySerializer
    filterset_fields = ['operation_type', 'activity_type']
    search_fields = ['name']

    def get_queryset(self):
        """
        Если категории общие — возвращаем все.
        Если нужно привязать категории к компании —
        тогда фильтруем их по company или используем сервис.
        """
        return Category.objects.all()
        # Или (если у Category есть поле company):
        # company = getattr(self.request, 'current_company', None)
        # if not company:
        #     return Category.objects.none()
        # return Category.objects.filter(company=company)


class ActivityTypeViewSet(BaseViewSet):
    serializer_class = ActivityTypeSerializer
    search_fields = ['name']

    def get_queryset(self):
        """
        Аналогично Category. Если ActivityType глобальны, возвращаем все.
        Если нужно привязать к company, фильтруем (или используем сервис).
        """
        return ActivityType.objects.prefetch_related('categories')