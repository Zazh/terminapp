from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import ReportViewSet, AnalyticsViewSet

router = DefaultRouter()
router.register(r'reports', ReportViewSet)
router.register(r'analytics', AnalyticsViewSet, basename='analytics')

urlpatterns = [
    path('', include(router.urls)),
]