from django import forms
from .models import Product, ProductCategory, Specification, ProductSpecification


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "description", "product_type", "category", "price"]


class CategoryForm(forms.ModelForm):
    class Meta:
        model = ProductCategory
        fields = ["name", "description"]


class SpecificationForm(forms.ModelForm):
    class Meta:
        model = Specification
        fields = ["name", "description"]


class ProductSpecificationForm(forms.ModelForm):
    class Meta:
        model = ProductSpecification
        fields = ["specification", "value"]
