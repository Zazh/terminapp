from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.exceptions import ValidationError  # Добавить в импорты
from django.utils.translation import gettext_lazy as _  # Добавить этот импорт
import re


class UserManager(BaseUserManager):
    def create_user(self, identifier_field, identifier_value, password=None, **extra_fields):
        """
        Универсальный метод создания пользователя
        """
        if not identifier_value:
            raise ValueError(_("User must have at least one identifier"))

        user = self.model(**{identifier_field: identifier_value}, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_client(self, phone_number, password=None, **extra_fields):
        if not re.match(r'^\+?1?\d{9,15}$', phone_number):
            raise ValueError(_("Invalid phone number format"))

        return self.create_user(
            identifier_field='phone_number',
            identifier_value=phone_number,
            password=password,
            role=User.Role.CLIENT,
            **extra_fields
        )

    def create_staff(self, email, password=None, **extra_fields):
        if not email.endswith('@company.com'):
            raise ValueError(_("Only company emails allowed"))

        return self.create_user(
            identifier_field='email',
            identifier_value=email,
            password=password,
            role=User.Role.STAFF,
            **extra_fields
        )

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', User.Role.ADMIN)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(
            identifier_field='email',
            identifier_value=email,
            password=password,
            **extra_fields
        )


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        CLIENT = 'CLIENT', _('Client')
        STAFF = 'STAFF', _('Staff')
        ADMIN = 'ADMIN', _('Admin')

    username = models.CharField(
        max_length=150,
        unique=True,
        null=True,
        blank=True,
        default=None,
        error_messages={'unique': _("A user with that username already exists.")}
    )
    email = models.EmailField(
        unique=True,
        null=True,
        blank=True,
        default=None,
        error_messages={'unique': _("A user with that email already exists.")}
    )
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        null=True,
        blank=True,
        default=None,
        error_messages={'unique': _("A user with that phone number already exists.")}
    )

    role = models.CharField(
        max_length=7,
        choices=Role.choices,
        default=Role.CLIENT
    )

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['email'],
                name='unique_email',
                condition=models.Q(email__isnull=False)
            ),
            models.UniqueConstraint(
                fields=['phone_number'],
                name='unique_phone',
                condition=models.Q(phone_number__isnull=False)
            ),
            models.UniqueConstraint(
                fields=['username'],
                name='unique_username',
                condition=models.Q(username__isnull=False)
            )
        ]
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['username']),
        ]

    def __str__(self):
        return self.get_identifier()

    def get_identifier(self):
        return self.email or self.phone_number or self.username

    def clean(self):
        if not any([self.email, self.phone_number, self.username]):
            raise ValidationError(_("At least one identifier must be provided"))

    @property
    def is_client(self):
        return self.role == self.Role.CLIENT

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN