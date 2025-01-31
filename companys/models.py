# tenant/models.py
from django.db import models

class Company(models.Model):
    """
    Модель, отвечающая за компанию (Tenant).
    """
    name = models.CharField(max_length=255, unique=True)
    subdomain = models.CharField(max_length=50, blank=True, null=True, unique=True)
    billing_plan = models.CharField(max_length=50, default='basic')
    created_at = models.DateTimeField(auto_now_add=True)
    # Могут быть другие поля: тариф, лого и т.д.

    def __str__(self):
        return self.name
