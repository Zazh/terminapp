# services.py
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import (
    ProductCategory,
    Product,
    PriceList,
    BusinessDirection
)


def create_business_direction(name: str, description: str = "") -> BusinessDirection:
    """
    Пример бизнес-логики для создания направления бизнеса (BusinessDirection).
    """
    if not name:
        raise ValidationError("Business direction name is required.")

    bd = BusinessDirection.objects.create(
        name=name,
        description=description
    )
    return bd


@transaction.atomic
def create_product_category(
        company,
        name: str,
        business_direction_id: int = None,
        description: str = ""
) -> ProductCategory:
    """
    Создание категории продукта для конкретной компании.
    При необходимости можно валидировать доступ пользователя к company.
    """
    if not name:
        raise ValidationError("Category name is required.")

    # Проверяем, есть ли у нас переданный business_direction
    business_direction = None
    if business_direction_id:
        try:
            business_direction = BusinessDirection.objects.get(pk=business_direction_id)
        except BusinessDirection.DoesNotExist:
            raise ValidationError("BusinessDirection with the provided ID does not exist.")

    # Создаём категорию
    category = ProductCategory.objects.create(
        company=company,
        business_direction=business_direction,
        name=name,
        description=description
    )
    return category


@transaction.atomic
def create_product(
        company,
        category_id: int,
        name: str,
        sku: str,
        is_bookable: bool,
        product_type: str = 'product',
        initial_price: float = None,
        currency: str = 'KZT'
) -> Product:
    """
    Пример создания продукта.
    Также сразу можем добавить запись в PriceList, если передана цена.
    """
    if not name:
        raise ValidationError("Product name is required.")
    if not sku:
        raise ValidationError("SKU is required.")

    # Получаем категорию
    try:
        category = ProductCategory.objects.get(pk=category_id, company=company)
    except ProductCategory.DoesNotExist:
        raise ValidationError("ProductCategory with the provided ID does not exist or doesn't belong to this company.")

    product = Product.objects.create(
        company=company,
        category=category,
        name=name,
        sku=sku,
        is_bookable=is_bookable,
        product_type=product_type
    )

    # Если есть начальная цена, то создаём объект PriceList
    if initial_price is not None:
        PriceList.objects.create(
            company=company,
            product=product,
            price=initial_price,
            currency=currency
        )

    return product