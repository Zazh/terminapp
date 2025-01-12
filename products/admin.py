from django.contrib import admin
from .models import ProductCategory, Product, Specification, ProductSpecification


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at',)

class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1
    autocomplete_fields = ('specification',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_type', 'category', 'price', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('product_type', 'category', 'created_at')
    autocomplete_fields = ('category',)
    ordering = ('-created_at',)
    inlines = [ProductSpecificationInline]


@admin.register(Specification)
class SpecificationAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at',)


@admin.register(ProductSpecification)
class ProductSpecificationAdmin(admin.ModelAdmin):
    list_display = ('product', 'specification', 'value', 'created_at', 'updated_at')
    search_fields = ('product__name', 'specification__name', 'value')
    list_filter = ('product', 'specification', 'created_at')
    autocomplete_fields = ('product', 'specification')