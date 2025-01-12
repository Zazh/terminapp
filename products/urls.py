from django.urls import path
from .views import (
    ProductListView,
    ProductDetailView,
    ProductCreateView,
    ProductUpdateView,
    CategoryListView,
    CategoryCreateView,
    CategoryUpdateView,
    SpecificationCreateView,
    SpecificationUpdateView,
    SpecificationListView,
    ProductSpecificationCreateView,
)

app_name = "products"

urlpatterns = [
    path("", ProductListView.as_view(), name="product_list"),
    path("product/<int:pk>/", ProductDetailView.as_view(), name="product_detail"),
    path("product/add/", ProductCreateView.as_view(), name="product_create"),
    path("product/<int:pk>/edit/", ProductUpdateView.as_view(), name="product_update"),
    path("categories/", CategoryListView.as_view(), name="category_list"),
    path("category/add/", CategoryCreateView.as_view(), name="category_create"),
    path("category/<int:pk>/edit/", CategoryUpdateView.as_view(), name="category_update"),
    path("specification/add/", SpecificationCreateView.as_view(), name="specification_create"),
    path("specification/<int:pk>/edit/", SpecificationUpdateView.as_view(), name="specification_update"),
    path("specifications/", SpecificationListView.as_view(), name="specifications_list"),
    path("product/<int:product_id>/specification/add/", ProductSpecificationCreateView.as_view(), name="product_specification_create"),
]
