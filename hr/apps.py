# hr/apps.py

from django.apps import AppConfig

class HrConfig(AppConfig):
    name = 'hr'
    verbose_name = 'HR Application'

    def ready(self):
        import hr.signals  # noqa
