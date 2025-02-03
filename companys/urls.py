from django.urls import path
from .api import CompanyCreateAPIView

urlpatterns = [
    path('create/', CompanyCreateAPIView.as_view(), name='company-create'),
]