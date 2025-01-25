from django.urls import path
from .views import register_client, register_staff, CustomLoginView, profile
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('register/client/', register_client, name='register_client'),
    path('register/staff/', register_staff, name='register_staff'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('profile/', profile, name='profile'),
]