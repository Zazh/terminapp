# clients/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import ClientViewSet

router = DefaultRouter()
router.register(r'clients', ClientViewSet, basename='clients')

urlpatterns = [
    path('', include(router.urls)),
]