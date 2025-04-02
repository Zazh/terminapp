from django.urls import path
from .views import main_placeholder

urlpatterns = [
    path('', main_placeholder, name='main'),  # главная страница
]