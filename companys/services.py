# companys/services.py

from django.core.exceptions import ValidationError
from .models import Company

def create_company(owner, name: str, subdomain: str = None, billing_plan: str = 'basic') -> Company:
    """
    Создает новую компанию для пользователя owner.
    Если у данного пользователя уже есть компания, выбрасывает ошибку.
    После создания компании автоматически добавляет owner как Employee (Admin).
    """
    if Company.objects.filter(owner=owner).exists():
        raise ValidationError("A company for this user already exists.")

    company = Company(
        owner=owner,
        name=name,
        subdomain=subdomain,
        billing_plan=billing_plan
    )
    company.full_clean()  # Вызовет .clean() у модели Company
    company.save()

    # -- Автоматически создаём сотрудника-админа --
    from hr.services import create_owner_employee
    create_owner_employee(owner, company)

    return company