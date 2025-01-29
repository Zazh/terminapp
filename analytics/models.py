# analytics/models.py
from django.db import models


class Report(models.Model):
    """
    Сохранённые данные аналитических отчётов.
    """
    objects = None
    name = models.CharField("Название отчёта", max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    data = models.JSONField("Данные отчёта")

    def __str__(self):
        return self.name
