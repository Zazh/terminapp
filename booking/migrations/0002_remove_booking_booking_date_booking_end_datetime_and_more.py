# Generated by Django 5.1.3 on 2025-01-22 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='booking_date',
        ),
        migrations.AddField(
            model_name='booking',
            name='end_datetime',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Конец брони'),
        ),
        migrations.AddField(
            model_name='booking',
            name='start_datetime',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Начало брони'),
        ),
        migrations.AddField(
            model_name='bookingitem',
            name='end_datetime',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Конец брони (элемент)'),
        ),
        migrations.AddField(
            model_name='bookingitem',
            name='start_datetime',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Начало брони (элемент)'),
        ),
        migrations.AddField(
            model_name='bookingitem',
            name='status',
            field=models.CharField(choices=[('pending', 'В процессе'), ('confirmed', 'Подтверждено'), ('completed', 'Завершено'), ('cancelled', 'Отменено')], default='pending', max_length=20, verbose_name='Статус позиции'),
        ),
        migrations.AlterField(
            model_name='booking',
            name='status',
            field=models.CharField(choices=[('pending', 'В процессе'), ('confirmed', 'Подтверждено'), ('completed', 'Завершено'), ('cancelled', 'Отменено')], default='pending', max_length=20, verbose_name='Статус брони'),
        ),
    ]
