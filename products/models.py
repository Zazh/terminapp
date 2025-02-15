from django.db import models
from django.utils.translation import gettext_lazy as _
from hr.models import Company  # Импорт вашей модели компании

class ProductCategory(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="product_categories",
        verbose_name=_("Company")
    )
    name = models.CharField(max_length=255, verbose_name=_("Category Name"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        # Название категории должно быть уникально в пределах одной компании
        unique_together = ("company", "name")
        verbose_name = _("Product Category")
        verbose_name_plural = _("Product Categories")

    def __str__(self):
        return f"{self.name} (Company: {self.company.name})"


class Product(models.Model):
    PRODUCT_TYPE_CHOICES = [
        ('service', 'Service'),
        ('product', 'Product'),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name=_("Company")
    )
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
    product_type = models.CharField(
        max_length=10,
        choices=PRODUCT_TYPE_CHOICES,
        default='product',
        verbose_name=_("Product Type")
    )
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name=_("Category")
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Price"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        # Уникальность продукта (по имени и типу) проверяется в пределах компании
        constraints = [
            models.UniqueConstraint(
                fields=['company', 'category', 'name'],
                name='unique_product_name_in_category_per_company'
            )
        ]
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def __str__(self):
        return f"{self.name} (Company: {self.company.name})"


class Specification(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="specifications",
        verbose_name=_("Company")
    )
    name = models.CharField(max_length=255, verbose_name=_("Specification Name"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        unique_together = ("company", "name")
        verbose_name = _("Specification")
        verbose_name_plural = _("Specifications")

    def __str__(self):
        return f"{self.name} (Company: {self.company.name})"


class ProductSpecification(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="product_specifications",
        verbose_name=_("Product")
    )
    specification = models.ForeignKey(
        Specification,
        on_delete=models.CASCADE,
        related_name="product_specifications",
        verbose_name=_("Specification")
    )
    value = models.CharField(max_length=255, verbose_name=_("Value"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        # Каждая привязка (пара продукт-спецификация) должна быть уникальна
        unique_together = ("product", "specification")
        verbose_name = _("Product Specification")
        verbose_name_plural = _("Product Specifications")

    def __str__(self):
        return f"{self.product.name} - {self.specification.name}: {self.value}"
