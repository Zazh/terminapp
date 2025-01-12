from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from .models import Product, ProductCategory, Specification, ProductSpecification
from .forms import ProductForm, CategoryForm, SpecificationForm, ProductSpecificationForm


class ProductListView(ListView):
    model = Product
    template_name = "products/product_list.html"
    context_object_name = "products"
    paginate_by = 10

    def get_queryset(self):
        return Product.objects.select_related("category").all()


class ProductDetailView(DetailView):
    model = Product
    template_name = "products/product_detail.html"
    context_object_name = "product"


class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = "products/product_form.html"
    success_url = reverse_lazy("products:product_list")


class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "products/product_form.html"
    success_url = reverse_lazy("products:product_list")


class CategoryListView(ListView):
    model = ProductCategory
    template_name = "products/category_list.html"
    context_object_name = "categories"
    paginate_by = 10  # Добавьте пагинацию, если нужно

class CategoryUpdateView(UpdateView):
    model = ProductCategory
    form_class = CategoryForm
    template_name = "products/category_form.html"
    success_url = reverse_lazy("products:category_list")


class CategoryCreateView(CreateView):
    model = ProductCategory
    form_class = CategoryForm
    template_name = "products/category_form.html"
    success_url = reverse_lazy("products:category_list")


class SpecificationCreateView(CreateView):
    model = Specification
    form_class = SpecificationForm
    template_name = "products/specification_form.html"
    success_url = reverse_lazy("products:specifications_list")

class SpecificationListView(ListView):
    model = Specification
    template_name = "products/specifications_list.html"
    context_object_name = "specifications"

class SpecificationUpdateView(UpdateView):
    model = Specification
    form_class = SpecificationForm
    template_name = "products/specification_form.html"
    context_object_name = "specification"

    def get_object(self, queryset=None):
        """Получить объект характеристики по ID"""
        return get_object_or_404(Specification, pk=self.kwargs["pk"])

    def get_success_url(self):
        """URL для перенаправления после успешного обновления"""
        return reverse_lazy("products:specifications_list")

class ProductSpecificationCreateView(CreateView):
    model = ProductSpecification
    form_class = ProductSpecificationForm
    template_name = "products/product_specification_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = get_object_or_404(Product, id=self.kwargs['product_id'])
        return context

    def form_valid(self, form):
        form.instance.product = get_object_or_404(Product, id=self.kwargs["product_id"])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("products:product_detail", kwargs={"pk": self.kwargs["product_id"]})
