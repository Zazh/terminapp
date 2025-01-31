# account/urls.py

from django.urls import path
from .api import (
    RegisterAPIView,
    LoginAPIView,
    LogoutAPIView,
    ProfileAPIView
)

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('profile/', ProfileAPIView.as_view(), name='profile'),
]
