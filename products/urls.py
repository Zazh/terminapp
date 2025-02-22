# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import (
    BusinessDirectionViewSet,
    ProductCategoryViewSet,
    ProductViewSet,
)

router = DefaultRouter()
router.register('business-directions', BusinessDirectionViewSet, basename='business-direction')
router.register('product-categories', ProductCategoryViewSet, basename='product-category')
router.register('products', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
]