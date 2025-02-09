# Generated by Django 5.1.3 on 2025-01-22 11:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('orders', '0020_alter_orderitem_order'),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('booking_date', models.DateField(verbose_name='Дата брони')),
                ('status', models.CharField(choices=[('pending', 'В процессе'), ('confirmed', 'Подтверждено'), ('cancelled', 'Отменено'), ('completed', 'Завершено')], default='pending', max_length=20, verbose_name='Статус')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='orders.order', verbose_name='Заказ')),
            ],
            options={
                'verbose_name': 'Бронирование',
                'verbose_name_plural': 'Бронирования',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='BookingItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1, verbose_name='Забронированное количество')),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='booking_items', to='booking.booking', verbose_name='Бронирование')),
                ('order_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='orders.orderitem', verbose_name='Позиция заказа')),
            ],
            options={
                'verbose_name': 'Позиция бронирования',
                'verbose_name_plural': 'Позиции бронирования',
            },
        ),
    ]
