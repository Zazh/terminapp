from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Базовый метод создания пользователя.
        Аутентификация по email, поэтому email обязателен.
        """
        if not email:
            raise ValueError(_("Users must have an email address"))

        email = self.normalize_email(email)

        # Проверка длины email
        if len(email) > 254:
            raise ValidationError(_("Email is too long (maximum 254 characters)."))

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.full_clean()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Создаёт суперпользователя (is_staff, is_superuser = True).
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Упрощённая модель пользователя с email-аутентификацией.
    Поля username, phone_number, role удалены.
    """
    email = models.EmailField(
        unique=True,
        null=False,
        blank=False,
        max_length=254,
        error_messages={'unique': _("A user with that email already exists.")}
    )

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # При создании суперпользователя из CLI не спрашиваем ничего кроме email

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        return self.email

    def clean(self):
        """
        Валидация перед сохранением объекта.
        """
        super().clean()

        # Проверяем email на корректный формат
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex, self.email):
            raise ValidationError(_("Invalid email format."))

        # Убеждаемся, что email всегда в нижнем регистре
        self.email = self.email.lower().strip()

    def save(self, *args, **kwargs):
        """
        Гарантирует, что email всегда сохраняется в нижнем регистре.
        """
        self.email = self.email.lower().strip()
        super().save(*args, **kwargs)

    @property
    def is_admin(self):
        """Проверяет, является ли пользователь администратором."""
        return self.is_superuser

    @property
    def is_employee(self):
        """Проверяет, является ли пользователь сотрудником (но не суперпользователем)."""
        return self.is_staff and not self.is_superuser
