from rest_framework import serializers
from .models import (
    ProductCategory,
    Product,
    Specification,
    ProductSpecification
)

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductSerializer(serializers.ModelSerializer):
    # Можем отобразить название категории, если нужно
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'product_type',
            'price',
            'created_at',
            'updated_at',
            'category',
            'category_name'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'category_name']


class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductSpecificationSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    specification_name = serializers.CharField(source='specification.name', read_only=True)

    class Meta:
        model = ProductSpecification
        fields = [
            'id',
            'product',
            'specification',
            'value',
            'product_name',
            'specification_name',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'product_name', 'specification_name']
