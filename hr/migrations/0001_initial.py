# Generated by Django 5.1.3 on 2025-02-12 15:04

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('subdomain', models.CharField(blank=True, help_text='Введите поддомен, состоящий только из маленьких латинских букв, цифр и дефисов.', max_length=50, null=True, unique=True)),
                ('billing_plan', models.CharField(default='basic', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('owner', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='company', to=settings.AUTH_USER_MODEL, verbose_name='Owner')),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('code', models.CharField(blank=True, max_length=50, null=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='departments', to='hr.company')),
            ],
            options={
                'verbose_name': 'Department',
                'verbose_name_plural': 'Departments',
                'unique_together': {('company', 'name')},
            },
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('ACTIVE', 'Active'), ('FIRED', 'Fired'), ('ON_LEAVE', 'On Leave')], default='ACTIVE', max_length=20)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employees', to='hr.company')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='employee_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Employee',
                'verbose_name_plural': 'Employees',
                'permissions': (('can_approve_vacation', 'Can approve vacation requests'), ('can_manage_salaries', 'Can manage salaries')),
            },
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
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='roles', to='hr.company')),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='roles', to='hr.department')),
                ('groups', models.ManyToManyField(blank=True, related_name='hr_roles', to='auth.group')),
            ],
            options={
                'verbose_name': 'Role',
                'verbose_name_plural': 'Roles',
                'unique_together': {('company', 'name')},
            },
        ),
        migrations.AddField(
            model_name='employee',
            name='roles',
            field=models.ManyToManyField(blank=True, related_name='employees', to='hr.role'),
        ),
    ]
