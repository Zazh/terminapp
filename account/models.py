# models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

class AccountManager(BaseUserManager):
    def create_user(self, username=None, email=None, phone_number=None, password=None, **extra_fields):
        if not username and not email and not phone_number:
            raise ValueError(_('Users must have a username, email, or phone number.'))

        # Логика для суперпользователя
        if extra_fields.get('is_superuser'):
            if not username:
                raise ValueError(_('Superuser must have a username.'))
            user = self.model(username=username, email=email, **extra_fields)

        # Логика для сотрудников
        elif extra_fields.get('is_staff'):
            if not email:
                raise ValueError(_('Staff must have an email address.'))
            user = self.model(username=username, email=email, **extra_fields)

        # Логика для клиентов
        else:
            if not phone_number:
                raise ValueError(_('Clients must have a phone number.'))
            user = self.model(username=username, phone_number=phone_number, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        if not username:
            raise ValueError(_('Superuser must have a username.'))

        return self.create_user(username=username, email=email, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)

    is_client = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = AccountManager()

    USERNAME_FIELD = 'username'  # Определяет основное поле для аутентификации
    REQUIRED_FIELDS = ['email']  # Указывает дополнительные обязательные поля для суперпользователя

    def __str__(self):
        return self.username or self.email or self.phone_number

    def save(self, *args, **kwargs):
        if self.is_staff and not self.email:
            raise ValueError(_('Staff must have an email address.'))
        if self.is_client and not self.phone_number:
            raise ValueError(_('Clients must have a phone number.'))
        super().save(*args, **kwargs)
