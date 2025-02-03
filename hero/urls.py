from django.urls import path, include
from .views import main_placeholder

urlpatterns = [
    path('', main_placeholder, name='main'),  # главная страница
]