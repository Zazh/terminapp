# api.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
# Если у вас есть свои кастомные пермишены для мультиарендности, добавляйте их
# from .permissions import IsCompanyMember

from .models import BusinessDirection, ProductCategory, Product
from .serializers import (
    BusinessDirectionSerializer,
    ProductCategorySerializer,
    ProductSerializer
)
from .services import (
    create_business_direction,
    create_product_category,
    create_product
)


class BusinessDirectionViewSet(viewsets.ModelViewSet):
    """
    Пример CRUD для BusinessDirection.
    """
    queryset = BusinessDirection.objects.all()
    serializer_class = BusinessDirectionSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Переопределяем create, чтобы использовать сервис.
        Можно оставить стандартное поведение, но здесь
        показано, как это выглядит через сервис-слой.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        name = serializer.validated_data.get('name')
        description = serializer.validated_data.get('description', "")

        bd = create_business_direction(name=name, description=description)

        # Возвращаем результат через сериализатор
        output_serializer = self.get_serializer(bd)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class ProductCategoryViewSet(viewsets.ModelViewSet):
    """
    Пример CRUD для ProductCategory.
    """
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Можно фильтровать по company,
        чтобы не возвращать чужие категории в мультиарендной системе.
        """
        qs = super().get_queryset()
        # Предположим, что company доступна в request.user.company
        user_company = getattr(self.request.user, 'company', None)
        if user_company is not None:
            qs = qs.filter(company=user_company)
        return qs

    def create(self, request, *args, **kwargs):
        # Здесь можно вытащить `company` из пользователя,
        # если у вас так организована логика.
        user_company = getattr(request.user, 'company', None)
        if not user_company:
            return Response(
                {"detail": "User does not have a company assigned."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Сериализуем входные данные
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        name = serializer.validated_data.get('name')
        description = serializer.validated_data.get('description', "")
        business_direction = serializer.validated_data.get('business_direction', None)
        business_direction_id = business_direction.id if business_direction else None

        category = create_product_category(
            company=user_company,
            name=name,
            business_direction_id=business_direction_id,
            description=description
        )

        output_serializer = self.get_serializer(category)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class ProductViewSet(viewsets.ModelViewSet):
    """
    Пример CRUD для Product.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Фильтруем продукты по компании текущего пользователя.
        """
        qs = super().get_queryset()
        user_company = getattr(self.request.user, 'company', None)
        if user_company is not None:
            qs = qs.filter(company=user_company)
        return qs

    def create(self, request, *args, **kwargs):
        user_company = getattr(request.user, 'company', None)
        if not user_company:
            return Response(
                {"detail": "User does not have a company assigned."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        category_id = serializer.validated_data.get('category').id
        name = serializer.validated_data['name']
        sku = serializer.validated_data['sku']
        is_bookable = serializer.validated_data['is_bookable']
        product_type = serializer.validated_data.get('product_type', 'product')

        # Допустим, цену передаём опционально
        initial_price = request.data.get('initial_price', None)
        currency = request.data.get('currency', 'KZT')

        product = create_product(
            company=user_company,
            category_id=category_id,
            name=name,
            sku=sku,
            product_type=product_type,
            initial_price=initial_price,
            currency=currency,
            is_bookable=is_bookable
        )

        output_serializer = self.get_serializer(product)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)