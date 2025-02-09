# Generated by Django 5.1.3 on 2025-01-12 18:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cashflow', '0008_remove_transaction_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='transaction_type',
            field=models.CharField(choices=[('income', 'Доход'), ('expense', 'Расход')], default=1, max_length=10, verbose_name='Тип транзакции'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='transaction',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cashflow.category'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='wallet',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='cashflow.wallet', verbose_name='Кошелек'),
        ),
    ]
