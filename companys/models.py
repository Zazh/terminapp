# companys/models.py
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import re

class Company(models.Model):
    """
    Модель, отвечающая за компанию (Tenant).
    Каждый пользователь может создать только одну компанию, поэтому добавляем поле owner.
    """
    name = models.CharField(max_length=255, unique=True)
    subdomain = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        help_text=_("Введите поддомен, состоящий только из маленьких латинских букв, цифр и дефисов.")
    )
    billing_plan = models.CharField(max_length=50, default='basic')
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="company",
        verbose_name=_("Owner")
    )

    def clean(self):
        """
        Валидация перед сохранением.
        Если subdomain указан, убеждаемся, что он состоит только из маленьких букв, цифр и дефисов.
        """
        super().clean()
        if self.subdomain:
            regex_subdomain = r'^[a-z0-9-]+$'
            normalized = self.subdomain.lower().strip()
            if not re.match(regex_subdomain, normalized):
                raise ValidationError(_("Invalid subdomain format. It must contain only lowercase letters, numbers, and hyphens."))
            self.subdomain = normalized

    def __str__(self):
        return self.name
