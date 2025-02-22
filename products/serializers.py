# serializers.py
from rest_framework import serializers
from .models import (
    BusinessDirection,
    ProductCategory,
    Product,
    PriceList
)


class BusinessDirectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessDirection
        fields = '__all__'
        # Или перечислите нужные поля: fields = ("id", "name", "description")


class ProductCategorySerializer(serializers.ModelSerializer):
    business_direction = serializers.PrimaryKeyRelatedField(
        queryset=BusinessDirection.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = ProductCategory
        fields = '__all__'
        # Например: ("id", "name", "description", "business_direction", "company")


class PriceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceList
        fields = ("id", "price", "currency", "created_at", "updated_at")


class ProductSerializer(serializers.ModelSerializer):
    # Если нужно выводить связанную запись цены или категорию детально
    # можно использовать вложенные сериализаторы, но здесь для примера
    # оставим ссылку по PrimaryKey:
    category = serializers.PrimaryKeyRelatedField(
        queryset=ProductCategory.objects.all()
    )

    # Пример поля для чтения актуальной цены, если нужно
    current_price = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "sku",
            "product_type",
            "category",
            "company",
            "created_at",
            "updated_at",
            "current_price",
            "is_bookable"
        )

    def get_current_price(self, obj):
        return obj.get_current_price()