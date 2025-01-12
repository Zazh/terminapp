from django.db import models


class ProductCategory(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Category Name")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    def __str__(self):
        return self.name


class Product(models.Model):
    PRODUCT_TYPE_CHOICES = [
        ('service', 'Service'),
        ('product', 'Product'),
    ]

    name = models.CharField(max_length=255, verbose_name="Name")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    product_type = models.CharField(
        max_length=10,
        choices=PRODUCT_TYPE_CHOICES,
        default='product',
        verbose_name="Product Type"
    )
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Category"
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Price"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'product_type'],
                name='unique_product_by_type'
            )
        ]

    def __str__(self):
        return self.name


class Specification(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Specification Name")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    def __str__(self):
        return self.name


class ProductSpecification(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="product_specifications",
        verbose_name="Product"
    )
    specification = models.ForeignKey(
        Specification,
        on_delete=models.CASCADE,
        related_name="product_specifications",
        verbose_name="Specification"
    )
    value = models.CharField(max_length=255, verbose_name="Value")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    def __str__(self):
        return f"{self.product.name} - {self.specification.name}: {self.value}"

