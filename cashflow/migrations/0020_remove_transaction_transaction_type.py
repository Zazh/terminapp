# Generated by Django 5.1.3 on 2025-01-13 19:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cashflow', '0019_transaction_transaction_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='transaction_type',
        ),
    ]
