# admin_restrict/middleware.py

from django.http import HttpResponseForbidden
from django.conf import settings

class AdminRestrictMiddleware:
    """
    Ограничивает доступ к административной панели.
    Если запрос начинается с /admin и домен (Host) не равен admin.DOMAIN,
    возвращается 403 Forbidden.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0].lower().strip()
        # Генерируем административный домен на основе основного домена
        admin_domain = f"admin.{settings.DOMAIN}"
        if request.path.startswith('/admin') and host != admin_domain:
            return HttpResponseForbidden(
                f"Доступ к административной панели разрешён только с {admin_domain}"
            )
        return self.get_response(request)
