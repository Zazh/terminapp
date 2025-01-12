from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Product, ProductCategory, Specification, ProductSpecification


class ProductService:
    @staticmethod
    @transaction.atomic
    def create_product(name, product_type, category_id, price, description=None):
        """Создать товар или услугу."""
        category = ProductCategory.objects.filter(id=category_id).first()
        if not category:
            raise ValidationError("Category does not exist.")

        product = Product.objects.create(
            name=name,
            product_type=product_type,
            category=category,
            price=price,
            description=description
        )
        return product

    @staticmethod
    @transaction.atomic
    def update_product(product_id, **kwargs):
        """Обновить товар или услугу."""
        product = Product.objects.filter(id=product_id).first()
        if not product:
            raise ValidationError("Product does not exist.")

        for field, value in kwargs.items():
            if hasattr(product, field):
                setattr(product, field, value)
        product.save()
        return product

    @staticmethod
    def delete_product(product_id):
        """Удалить товар или услугу."""
        product = Product.objects.filter(id=product_id).first()
        if not product:
            raise ValidationError("Product does not exist.")
        product.delete()
        return True


class CategoryService:
    @staticmethod
    def create_category(name, description=None):
        """Создать категорию."""
        category = ProductCategory.objects.create(name=name, description=description)
        return category

    @staticmethod
    def update_category(category_id, **kwargs):
        """Обновить категорию."""
        category = ProductCategory.objects.filter(id=category_id).first()
        if not category:
            raise ValidationError("Category does not exist.")

        for field, value in kwargs.items():
            if hasattr(category, field):
                setattr(category, field, value)
        category.save()
        return category


class SpecificationService:
    @staticmethod
    def create_specification(name, description=None):
        """Создать характеристику."""
        specification = Specification.objects.create(name=name, description=description)
        return specification

    @staticmethod
    def assign_specification_to_product(product_id, specification_id, value):
        """Привязать характеристику к продукту."""
        product = Product.objects.filter(id=product_id).first()
        specification = Specification.objects.filter(id=specification_id).first()

        if not product:
            raise ValidationError("Product does not exist.")
        if not specification:
            raise ValidationError("Specification does not exist.")

        product_specification = ProductSpecification.objects.create(
            product=product,
            specification=specification,
            value=value
        )
        return product_specification

    @staticmethod
    def update_specification_value(product_spec_id, value):
        """Обновить значение характеристики."""
        product_spec = ProductSpecification.objects.filter(id=product_spec_id).first()
        if not product_spec:
            raise ValidationError("Product specification does not exist.")

        product_spec.value = value
        product_spec.save()
        return product_spec
