from .models import User

def create_client_user(phone_number, password=None, **extra_fields):
    """
    Тонкая обёртка над User.objects.create_client
    """
    return User.objects.create_client(phone_number=phone_number, password=password, **extra_fields)


def create_staff_user(email, password=None, **extra_fields):
    """
    Тонкая обёртка над User.objects.create_staff
    """
    return User.objects.create_staff(email=email, password=password, **extra_fields)


def create_superuser_account(username, email=None, password=None, **extra_fields):
    """
    Аналог для суперпользователя (обычно через shell).
    """
    return User.objects.create_superuser(username=username, email=email, password=password, **extra_fields)