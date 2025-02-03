# companys/services.py
from .models import Company
from django.core.exceptions import ValidationError

def create_company(owner, name: str, subdomain: str = None, billing_plan: str = 'basic') -> Company:
    """
    Создает новую компанию для пользователя owner.
    Если у данного пользователя уже есть компания, выбрасывается ошибка.
    """
    if Company.objects.filter(owner=owner).exists():
        raise ValidationError("A company for this user already exists.")
    company = Company(owner=owner, name=name, subdomain=subdomain, billing_plan=billing_plan)
    company.full_clean()  # Выполняет валидацию (включая метод clean)
    company.save()
    return company
