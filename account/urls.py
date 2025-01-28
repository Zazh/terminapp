# urls.py
from django.urls import path
from .views import register_client, register_staff, CustomLoginView, profile

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('register/client/', register_client, name='register_client'),
    path('register/staff/', register_staff, name='register_staff'),
    path('profile/', profile, name='profile'),
]