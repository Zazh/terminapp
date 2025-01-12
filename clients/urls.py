# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.client_list, name='client_list'),
    path('<int:client_id>/', views.client_detail, name='client_detail'),
    path('create/', views.client_create, name='client_create'),
    path('<int:client_id>/update/', views.client_update, name='client_update'),
    path('<int:client_id>/delete/', views.client_delete, name='client_delete'),
]