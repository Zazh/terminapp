# Generated by Django 5.1.3 on 2025-01-29 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_user_account_use_email_553b8f_idx_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'user', 'verbose_name_plural': 'users'},
        ),
        migrations.RemoveConstraint(
            model_name='user',
            name='unique_email',
        ),
        migrations.RemoveConstraint(
            model_name='user',
            name='unique_phone',
        ),
        migrations.RemoveConstraint(
            model_name='user',
            name='unique_username',
        ),
        migrations.RemoveIndex(
            model_name='user',
            name='account_use_email_553b8f_idx',
        ),
        migrations.RemoveIndex(
            model_name='user',
            name='account_use_phone_n_ed0b53_idx',
        ),
        migrations.RemoveIndex(
            model_name='user',
            name='account_use_usernam_19aad5_idx',
        ),
        migrations.RemoveField(
            model_name='user',
            name='phone_number',
        ),
        migrations.RemoveField(
            model_name='user',
            name='role',
        ),
        migrations.RemoveField(
            model_name='user',
            name='username',
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(error_messages={'unique': 'A user with that email already exists.'}, max_length=254, unique=True),
        ),
    ]
