# Generated by Django 5.1.3 on 2025-02-14 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hr', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='billing_plan',
            field=models.CharField(choices=[('TRIAL', 'TRIAL'), ('BASE', 'BASE')], default='BASE', max_length=50),
        ),
    ]
