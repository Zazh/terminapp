# Generated by Django 5.1.3 on 2025-02-14 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hr', '0002_alter_company_billing_plan'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='status',
            field=models.CharField(choices=[('ACTIVE', 'Active'), ('SUSPENDED', 'Suspended'), ('DELETED', 'DELETED')], default='ACTIVE', max_length=20),
        ),
        migrations.AlterField(
            model_name='company',
            name='billing_plan',
            field=models.CharField(choices=[('TRIAL', 'Trail'), ('BASE', 'Base')], default='BASE', max_length=50),
        ),
    ]
