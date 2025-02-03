# companys/middleware.py
from django.conf import settings
from .models import Company

class TenantMiddleware:
    """
    Извлекает subdomain из Host и устанавливает request.current_company.
    Если запрос идет на основной домен (например, DOMAIN или www.DOMAIN),
    фильтрация по тенанту не применяется — request.current_company устанавливается в None.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0]  # убираем порт
        host = host.lower().strip()

        # Получаем базовый домен из настроек
        base_domain = settings.DOMAIN  # например, "lvh.me"
        www_domain = f"www.{base_domain}"

        # Если запрос идёт на основной домен или www-домен, то не фильтруем
        if host == base_domain or host == www_domain:
            request.current_company = None
        else:
            # Если хост оканчивается на базовый домен, то, вероятно, присутствует субдомен
            if host.endswith("." + base_domain):
                # Извлекаем субдомен: удаляем из хоста ".{base_domain}"
                subdomain = host[:-len("." + base_domain)]
                # Если subdomain пустой — это что-то не то
                if not subdomain:
                    request.current_company = None
                else:
                    try:
                        company = Company.objects.get(subdomain=subdomain)
                        request.current_company = company
                    except Company.DoesNotExist:
                        # Если компания с таким субдоменом не найдена, можно вернуть ошибку,
                        # либо, как здесь, установить значение None.
                        request.current_company = None
            else:
                # Если хост не соответствует ожидаемому шаблону (например, другой домен),
                # можно задать request.current_company = None или вернуть ошибку.
                request.current_company = None

        return self.get_response(request)
