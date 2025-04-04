# Generated by Django 5.1.3 on 2025-02-15 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='primary_phone',
            field=models.CharField(help_text='Введите телефон в формате +79991234567', max_length=15, verbose_name='Основной телефон клиента'),
        ),
        migrations.AddConstraint(
            model_name='client',
            constraint=models.UniqueConstraint(fields=('company', 'primary_phone'), name='unique_phone_within_company'),
        ),
    ]
