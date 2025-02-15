from django.db import transaction
from django.core.exceptions import ValidationError

from .models import (
    Product,
    ProductCategory,
    Specification,
    ProductSpecification
)

class ProductService:
    @staticmethod
    @transaction.atomic
    def create_product(company, name, product_type, category_id, price, description=None):
        if not company:
            raise ValidationError("No company context found. Cannot create product.")

        category = ProductCategory.objects.filter(company=company, id=category_id).first()
        if not category:
            raise ValidationError("Category does not exist or does not belong to this company.")

        # -- Проверка уникальности в пределах (company, category, name) --
        if Product.objects.filter(company=company, category=category, name=name).exists():
            raise ValidationError("A product with this name already exists in the specified category.")

        product = Product.objects.create(
            company=company,
            name=name,
            product_type=product_type,
            category=category,
            price=price,
            description=description
        )
        return product

    @staticmethod
    @transaction.atomic
    def update_product(company, product_id, **kwargs):
        if not company:
            raise ValidationError("No company context found. Cannot update product.")

        product = Product.objects.filter(company=company, id=product_id).first()
        if not product:
            raise ValidationError("Product does not exist in this company.")

        # Если хотим сменить категорию
        new_category_id = kwargs.pop('category_id', None)
        if new_category_id:
            new_category = ProductCategory.objects.filter(company=company, id=new_category_id).first()
            if not new_category:
                raise ValidationError("New category does not exist in this company.")
            product.category = new_category

        # Обновляем остальные поля
        for field, value in kwargs.items():
            if hasattr(product, field):
                setattr(product, field, value)

        product.save()
        return product

    @staticmethod
    def delete_product(company, product_id):
        if not company:
            raise ValidationError("No company context found. Cannot delete product.")

        product = Product.objects.filter(company=company, id=product_id).first()
        if not product:
            raise ValidationError("Product does not exist in this company.")

        product.delete()
        return True


class CategoryService:
    @staticmethod
    def create_category(company, name, description=None):
        if not company:
            raise ValidationError("No company context found. Cannot create category.")

        category = ProductCategory.objects.create(
            company=company,
            name=name,
            description=description
        )
        return category

    @staticmethod
    def update_category(company, category_id, **kwargs):
        if not company:
            raise ValidationError("No company context found. Cannot update category.")

        category = ProductCategory.objects.filter(company=company, id=category_id).first()
        if not category:
            raise ValidationError("Category does not exist in this company.")

        for field, value in kwargs.items():
            if hasattr(category, field):
                setattr(category, field, value)
        category.save()
        return category


class SpecificationService:
    @staticmethod
    def create_specification(company, name, description=None):
        if not company:
            raise ValidationError("No company context found. Cannot create specification.")

        specification = Specification.objects.create(
            company=company,
            name=name,
            description=description
        )
        return specification

    @staticmethod
    def assign_specification_to_product(company, product_id, specification_id, value):
        if not company:
            raise ValidationError("No company context found. Cannot assign specification.")

        product = Product.objects.filter(company=company, id=product_id).first()
        if not product:
            raise ValidationError("Product does not exist in this company.")

        specification = Specification.objects.filter(company=company, id=specification_id).first()
        if not specification:
            raise ValidationError("Specification does not exist in this company.")

        product_specification = ProductSpecification.objects.create(
            product=product,
            specification=specification,
            value=value
        )
        return product_specification

    @staticmethod
    def update_specification_value(company, product_spec_id, value):
        if not company:
            raise ValidationError("No company context found. Cannot update specification value.")

        product_spec = ProductSpecification.objects.select_related('product', 'specification').filter(id=product_spec_id).first()
        if not product_spec:
            raise ValidationError("Product specification does not exist.")

        if product_spec.product.company != company:
            raise ValidationError("You do not have permission to update this specification (different company).")

        product_spec.value = value
        product_spec.save()
        return product_spec
