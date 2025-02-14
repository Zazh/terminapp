from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError

from .models import ProductCategory, Product, Specification, ProductSpecification
from .serializers import (
    ProductCategorySerializer,
    ProductSerializer,
    SpecificationSerializer,
    ProductSpecificationSerializer
)
from .services import (
    CategoryService,
    ProductService,
    SpecificationService
)

class TenantModelViewSet(viewsets.ModelViewSet):
    """
    Базовый класс ViewSet, который:
      1) Переопределяет get_queryset() для фильтрации по компании.
      2) Обрабатывает ошибки валидации.
      3) Реализует метод get_company() с проверкой соответствия компании из мидлвари и компании пользователя.
    """
    permission_classes = [IsAuthenticated]

    def get_company(self):
        # Получаем значение, установленное мидлваром (например, по субдомену)
        middleware_company = getattr(self.request, 'current_company', None)
        # Получаем компанию, связанную с аутентифицированным пользователем
        user_company = getattr(self.request.user, 'company', None)
        print(f"DEBUG: middleware_company = {middleware_company}, user_company = {user_company}")
        # Если определён мидлварный вариант, то проверяем соответствие с компанией пользователя
        if middleware_company and user_company:
            if middleware_company != user_company:
                # Можно либо вернуть ошибку, либо выбрать приоритет одного из значений.
                raise ValidationError("Access denied: wrong subdomain for your company.")
            return middleware_company

        # Если мидлвар не определил компанию, возвращаем компанию пользователя (если она есть)
        return user_company

    def get_queryset(self):
        qs = super().get_queryset()
        company = self.get_company()
        if company:
            return qs.filter(company=company)
        return qs.none()

    def handle_exception(self, exc):
        if isinstance(exc, ValidationError):
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return super().handle_exception(exc)


class ProductCategoryViewSet(TenantModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer

    def perform_create(self, serializer):
        company = self.get_company()
        data = serializer.validated_data
        category = CategoryService.create_category(
            company=company,
            name=data['name'],
            description=data.get('description')
        )
        serializer.instance = category

    def perform_update(self, serializer):
        company = self.get_company()
        category_id = self.kwargs.get('pk')
        data = serializer.validated_data
        updated_category = CategoryService.update_category(
            company=company,
            category_id=category_id,
            **data
        )
        serializer.instance = updated_category


class ProductViewSet(TenantModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def perform_create(self, serializer):
        company = self.get_company()
        data = serializer.validated_data
        product = ProductService.create_product(
            company=company,
            name=data['name'],
            product_type=data['product_type'],
            category_id=data['category'].id,
            price=data['price'],
            description=data.get('description')
        )
        serializer.instance = product

    def perform_update(self, serializer):
        company = self.get_company()
        product_id = self.kwargs.get('pk')
        data = serializer.validated_data
        if 'category' in data and data['category'] is not None:
            data['category_id'] = data['category'].id
            data.pop('category')
        updated_product = ProductService.update_product(
            company=company,
            product_id=product_id,
            **data
        )
        serializer.instance = updated_product


class SpecificationViewSet(TenantModelViewSet):
    queryset = Specification.objects.all()
    serializer_class = SpecificationSerializer

    def perform_create(self, serializer):
        company = self.get_company()
        data = serializer.validated_data
        specification = SpecificationService.create_specification(
            company=company,
            name=data['name'],
            description=data.get('description')
        )
        serializer.instance = specification

    def perform_update(self, serializer):
        company = self.get_company()
        spec_id = self.kwargs.get('pk')
        data = serializer.validated_data
        specification = self.get_queryset().filter(pk=spec_id).first()
        if not specification:
            raise ValidationError("Specification does not exist in this company.")
        for field, value in data.items():
            setattr(specification, field, value)
        specification.save()
        serializer.instance = specification


class ProductSpecificationViewSet(TenantModelViewSet):
    queryset = ProductSpecification.objects.select_related('product', 'specification').all()
    serializer_class = ProductSpecificationSerializer

    def get_queryset(self):
        # Вместо стандартной фильтрации по полю "company" (которое отсутствует),
        # фильтруем по компании, указанной в связанном поле product
        company = self.get_company()
        qs = ProductSpecification.objects.select_related('product', 'specification').all()
        if company:
            return qs.filter(product__company=company)
        return qs.none()

    def perform_create(self, serializer):
        company = self.get_company()
        data = serializer.validated_data
        # Здесь используем сервисный слой для создания привязки, он должен проверять, что
        # продукт принадлежит компании (через product_id, specification_id, и так далее)
        product_id = data['product'].id
        specification_id = data['specification'].id
        value = data['value']

        product_spec = SpecificationService.assign_specification_to_product(
            company=company,
            product_id=product_id,
            specification_id=specification_id,
            value=value
        )
        serializer.instance = product_spec

    def perform_update(self, serializer):
        company = self.get_company()
        ps_id = self.kwargs.get('pk')
        data = serializer.validated_data

        updated_spec = SpecificationService.update_specification_value(
            company=company,
            product_spec_id=ps_id,
            value=data['value']
        )
        serializer.instance = updated_spec
