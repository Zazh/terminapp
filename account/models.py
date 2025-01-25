from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _


class AccountManager(BaseUserManager):
    def create_user(self, username=None, email=None, phone_number=None, password=None, **extra_fields):
        """
        Базовый метод для создания пользователя без дополнительных флагов.
        """
        if not (username or email or phone_number):
            raise ValueError(_("Users must have a username, email, or phone number."))

        user = self.model(
            username=username,
            email=email,
            phone_number=phone_number,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_client(self, phone_number, password=None, **extra_fields):
        """
        Создание клиента (is_client=True).
        Предполагаем, что клиент регистрируется по номеру телефона.
        """
        if not phone_number:
            raise ValueError(_("Clients must have a phone number."))
        extra_fields.setdefault('is_client', True)
        return self.create_user(phone_number=phone_number, password=password, **extra_fields)

    def create_staff(self, email, password=None, **extra_fields):
        """
        Создание сотрудника (is_staff=True).
        Требуем обязательный email.
        """
        if not email:
            raise ValueError(_("Staff must have an email address."))
        extra_fields.setdefault('is_staff', True)
        return self.create_user(email=email, password=password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """
        Создание суперпользователя (через `createsuperuser`).
        Требуем обязательный username (и email — согласно вашему REQUIRED_FIELDS).
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not username:
            raise ValueError(_("Superuser must have a username."))

        return self.create_user(username=username, email=email, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)

    # Роли
    is_client = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = AccountManager()

    USERNAME_FIELD = 'username'       # для аутентификации через username
    REQUIRED_FIELDS = ['email']       # дополнительные поля при createsuperuser

    def __str__(self):
        return self.username or self.email or self.phone_number

    def save(self, *args, **kwargs):
        # Здесь не проводим "жёстких" проверок, они уже в менеджере.
        super().save(*args, **kwargs)