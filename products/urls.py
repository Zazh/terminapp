from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api import (
    ProductViewSet,
    ProductCategoryViewSet,
    SpecificationViewSet,
    ProductSpecificationViewSet,
)

app_name = "products"

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', ProductCategoryViewSet, basename='category')
router.register(r'specifications', SpecificationViewSet, basename='specification')
router.register(r'product-specifications', ProductSpecificationViewSet, basename='product-specification')

urlpatterns = [
    path("", include(router.urls)),
]
