from django.db import models
from hr.models import Company

class Client(models.Model):
    first_name = models.CharField(max_length=255, verbose_name="Имя клиента")
    primary_phone = models.CharField(
        max_length=15,
        verbose_name="Основной телефон клиента",
        help_text="Введите телефон в формате +75551234567"
    )
    backup_phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name="Резервный телефон"
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="clients",
        verbose_name="Компания"
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="E-mail"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['company', 'primary_phone'],
                name='unique_phone_within_company'
            )
        ]
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self):
        print(f"__str__ вызван для {self.first_name} с основным телефоном {self.primary_phone}")
        return f"{self.first_name} ({self.primary_phone})"