# Generated by Django 5.1.3 on 2025-01-13 17:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_alter_order_total_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='status',
            field=models.CharField(choices=[('pending', 'В ожидании'), ('completed', 'Завершен'), ('cancelled', 'Отменен'), ('refund', 'Возврат средств')], default='pending', max_length=20),
        ),
    ]
