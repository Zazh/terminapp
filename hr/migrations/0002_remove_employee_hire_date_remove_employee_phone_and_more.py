# Generated by Django 5.1.3 on 2025-01-30 18:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hr', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employee',
            name='hire_date',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='phone',
        ),
        migrations.AddField(
            model_name='employee',
            name='status',
            field=models.CharField(choices=[('ACTIVE', 'Active'), ('FIRED', 'Fired'), ('ON_LEAVE', 'On Leave')], default='ACTIVE', max_length=20),
        ),
        migrations.CreateModel(
            name='EmployeeInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('hire_date', models.DateField(blank=True, null=True)),
                ('employee', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='info', to='hr.employee')),
            ],
            options={
                'verbose_name': 'Employee Info',
                'verbose_name_plural': 'Employees Info',
            },
        ),
    ]
