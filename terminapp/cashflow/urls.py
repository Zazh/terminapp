from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import (
    TransactionViewSet,
    WalletViewSet,
    CategoryViewSet,
    ActivityTypeViewSet
)

router = DefaultRouter()
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'wallets', WalletViewSet, basename='wallet')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'activity-types', ActivityTypeViewSet, basename='activity-type')

urlpatterns = [
    path('', include(router.urls)),
]