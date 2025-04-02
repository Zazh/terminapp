# companys/middleware.py
from django.conf import settings
from django.http import Http404
from hr.models import Company


class TenantMiddleware:
    """
    Извлекает subdomain из Host и устанавливает request.current_company.

    Правила:
      - Если запрос идёт на главный домен (например, lvh.me или www.lvh.me) – не фильтруем, current_company = None.
      - Если запрос идёт на админку (admin.lvh.me) – не фильтруем, current_company = None.
      - Если запрос идёт на API (api.lvh.me) – используем fallback: если пользователь аутентифицирован и у него есть company, то current_company = request.user.company.
      - Если запрос идёт на любой другой судомоен (например, companyA.lvh.me) – ищем компанию по subdomain.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0].lower().strip()  # убираем порт, приводим к нижнему регистру

        base_domain = settings.DOMAIN  # например, "lvh.me"
        www_domain = f"www.{base_domain}"
        admin_domain = f"admin.{base_domain}"
        api_domain = f"api.{base_domain}"

        if host in [base_domain, www_domain]:
            # Главный домен (посадочная страница)
            request.current_company = None
        elif host == admin_domain:
            # Админка
            request.current_company = None
        elif host == api_domain:
            # API-домен: если пользователь аутентифицирован и имеет связанную компанию, используем её
            if hasattr(request, "user") and request.user.is_authenticated:
                request.current_company = getattr(request.user, "company", None)
            else:
                request.current_company = None
        elif host.endswith("." + base_domain):
            # Любой другой субдомен – предполагается, что это tenant-субдомен
            subdomain = host[:-len("." + base_domain)]
            if subdomain:
                try:
                    company = Company.objects.get(subdomain=subdomain)
                    request.current_company = company
                except Company.DoesNotExist:
                    raise Http404("Компания с таким субдоменом не найдена.")
            else:
                request.current_company = None
        else:
            # Если домен не соответствует ни одному из шаблонов
            request.current_company = None

        return self.get_response(request)
