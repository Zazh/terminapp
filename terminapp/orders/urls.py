# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import OrderViewSet, OrderItemViewSet, OrderItemRefundViewSet

app_name = 'orders'  # <-- ВАЖНО

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='orders')
router.register(r'order-items', OrderItemViewSet, basename='order-items')
router.register(r'refunds', OrderItemRefundViewSet, basename='refunds')


urlpatterns = [
    path('', include(router.urls)),
]
