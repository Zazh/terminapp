# Generated by Django 5.1.3 on 2025-02-22 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_product_is_bookable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pricelist',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Price'),
        ),
        migrations.AlterField(
            model_name='product',
            name='sku',
            field=models.CharField(max_length=12, verbose_name='SKU'),
        ),
    ]
