# account/services.py

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


def create_new_user(email: str, password: str, **extra_fields) -> User:
    """
    Бизнес-логика создания нового пользователя.
    Сюда можно добавить проверку уникальности email,
    дополнительные поля и т.д.
    """
    if not email:
        raise ValidationError("Email is required")

    # Создаём пользователя
    user = User.objects.create_user(email=email, password=password, **extra_fields)
    return user


def authenticate_user(email: str, password: str):
    """
    Простая функция для аутентификации;
    возвращает пользователя или None.
    Можно использовать EmailAuthBackend напрямую.
    """
    from account.authentication import EmailAuthBackend
    backend = EmailAuthBackend()
    return backend.authenticate(request=None, email=email, password=password)

