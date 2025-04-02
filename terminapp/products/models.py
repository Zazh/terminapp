from django.db import models
from django.utils.translation import gettext_lazy as _
from hr.models import Company

class BusinessDirection(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name=_("Business Direction"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))

    class Meta:
        verbose_name = _("Business Direction")
        verbose_name_plural = _("Business Directions")

    def __str__(self):
        return self.name


class ProductCategory(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="product_categories",
        verbose_name=_("Company")
    )
    business_direction = models.ForeignKey(
        BusinessDirection,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="product_categories",
        verbose_name=_("Business Direction")
    )
    name = models.CharField(max_length=255, verbose_name=_("Category Name"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        unique_together = ("company", "name")
        verbose_name = _("Product Category")
        verbose_name_plural = _("Product Categories")

    def __str__(self):
        return f"{self.name} (Company: {self.company.name})"


class Product(models.Model):
    PRODUCT_TYPE_CHOICES = [
        ('service', _('Service')),
        ('product', _('Product')),
    ]
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="product",
        verbose_name=_("Company")
    )
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        related_name="product",
        verbose_name=_("Category")
    )
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    is_bookable = models.BooleanField(default=False, verbose_name=_("Is Bookable"))
    product_type = models.CharField(
        max_length=10,
        choices=PRODUCT_TYPE_CHOICES,
        default='product',
        verbose_name=_("Product Type")
    )
    sku = models.CharField(max_length=12, verbose_name=_("SKU"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        unique_together = ('company', 'category', 'name')
        verbose_name = _("Product")
        verbose_name_plural = _("Product")

    def __str__(self):
        return f"{self.name} (SKU: {self.sku})"

    def get_current_price(self):
        """
        Возвращает актуальную цену продукта из PriceList.
        Берем последнюю запись по дате создания.
        """
        latest_price_entry = self.price_list.order_by('-created_at').first()
        if latest_price_entry:
            return latest_price_entry.price
        return None  # Если нет записей в PriceList, возвращаем None


class ProductInfo(models.Model):
    """
    Модель для хранения медиафайлов и дополнительной информации о продукте.
    """
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="product_info",
        verbose_name=_("Company")
    )
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='info',
        verbose_name=_("Product")
    )
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
    photo = models.ImageField(
        upload_to='product_photos/',
        blank=True,
        null=True,
        verbose_name=_("Photo")
    )
    # Дополнительные медиа-поля (видео, документы и т.д.) можно добавить по необходимости.
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Product Info")
        verbose_name_plural = _("Product Infos")

    def __str__(self):
        return f"{self.product.name} Info"


class Attribute(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="attributes",
        verbose_name=_("Company")
    )
    name = models.CharField(max_length=255, verbose_name=_("Attribute Name"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))

    class Meta:
        unique_together = ("company", "name")
        verbose_name = _("Attribute")
        verbose_name_plural = _("Attributes")

    def __str__(self):
        return self.name


class ProductAttributeValue(models.Model):
    """
    Хранит значения характеристик, привязанных к конкретному шаблону продукта.
    """
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="product_attributes_value",
        verbose_name=_("Company")
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='attributes',
        verbose_name=_("Product")
    )
    attribute = models.ForeignKey(
        Attribute,
        on_delete=models.CASCADE,
        related_name='product_values',
        verbose_name=_("Attribute")
    )
    value = models.CharField(max_length=255, verbose_name=_("Value"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        unique_together = ('product', 'attribute')
        verbose_name = _("Product Attribute Value")
        verbose_name_plural = _("Product Attribute Values")

    def __str__(self):
        return f"{self.product.name} - {self.attribute.name}: {self.value}"


# Прайс-лист для хранения информации о цене продукта
class PriceList(models.Model):
    CURRENCY_TYPE_CHOICES = [
        ('KZT', _('Тенге')),
        ('USD', _('$')),
    ]
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="price_list",
        verbose_name=_("Company")
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='price_list',
        verbose_name=_("Product")
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Price"), default=0)
    currency = models.CharField(
        max_length=10,
        choices=CURRENCY_TYPE_CHOICES,
        default='KZT',
        verbose_name=_("Currency")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))


    class Meta:
        verbose_name = _("Price List")
        verbose_name_plural = _("Price Lists")

    def __str__(self):
        return f"{self.product.name} - Price: {self.price} {self.currency}"