# hero/middleware.py
from django.conf import settings

class SwitchUrlConfMiddleware:
    """
    Если запрос поступает с основного домена (например, DOMAIN или www.DOMAIN),
    устанавливает альтернативный URLconf для отображения hero‑приложения.
    В противном случае оставляет стандартный URLconf.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0].lower().strip()
        base_domain = settings.DOMAIN  # например, "lvh.me"
        www_domain = f"www.{base_domain}"
        if host == base_domain or host == www_domain:
            # Используем URL-конфигурацию приложения hero
            request.urlconf = 'hero.urls'
        # Если же запрос пришёл с субдомена (например, alpha.lvh.me),
        # оставляем стандартный URLconf (из settings.ROOT_URLCONF)
        return self.get_response(request)
