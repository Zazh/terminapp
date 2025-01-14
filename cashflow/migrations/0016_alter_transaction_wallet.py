# Generated by Django 5.1.3 on 2025-01-13 18:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cashflow', '0015_remove_category_activity_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='wallet',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='cashflow.wallet', verbose_name='Кошелёк'),
        ),
    ]