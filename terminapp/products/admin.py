from django.contrib import admin
from .models import (
    BusinessDirection,
    ProductCategory,
    Product,
    ProductInfo,
    Attribute,
    ProductAttributeValue,
    PriceList,
)

@admin.register(BusinessDirection)
class BusinessDirectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'business_direction', 'created_at')
    search_fields = ('name',)
    list_filter = ('company', 'business_direction')


class ProductInfoInline(admin.StackedInline):
    model = ProductInfo
    extra = 0


class ProductAttributeValueInline(admin.TabularInline):
    model = ProductAttributeValue
    extra = 0


class PriceListInline(admin.TabularInline):
    model = PriceList
    fk_name = 'product'  # Явно указываем имя FK
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'sku',
        'company',
        'category',
        'product_type',
        'created_at'
    )
    search_fields = ('name', 'sku')
    list_filter = ('company', 'category', 'product_type')
    inlines = [ProductInfoInline, ProductAttributeValueInline, PriceListInline]


@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    list_display = ('product', 'created_at', 'company')
    search_fields = ('product__name', 'product__sku', 'company')


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ('name', 'company')
    search_fields = ('name',)
    list_filter = ('company',)


@admin.register(ProductAttributeValue)
class ProductAttributeValueAdmin(admin.ModelAdmin):
    list_display = ('product', 'attribute', 'value', 'created_at', 'company')
    search_fields = (
        'product__name',
        'attribute__name',
        'value',
        'company',
    )


@admin.register(PriceList)
class PriceListAdmin(admin.ModelAdmin):
    # Если прямой доступ к полю product вызывает ошибку,
    # определим метод, который возвращает нужное значение.
    list_display = ('product_name', 'price', 'currency','company')
    search_fields = ('product__name', 'company')
    list_filter = ('currency',)

    def product_name(self, obj):
        return obj.product.name
    product_name.short_description = "Product"