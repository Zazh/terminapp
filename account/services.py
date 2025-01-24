# services.py
from .models import User
from django.utils.translation import gettext_lazy as _

def create_user(self, username=None, email=None, phone_number=None, password=None, **extra_fields):
    if not username and not email and not phone_number:
        raise ValueError(_('Users must have a username, email, or phone number.'))

    extra_fields.setdefault('is_active', True)

    # Проверяем условия для разных типов пользователей
    if extra_fields.get('is_staff'):
        if not email:
            raise ValueError(_('Staff must have an email address.'))
        user = self.model(email=email, **extra_fields)
    elif extra_fields.get('is_superuser'):
        if not username:
            raise ValueError(_('Superuser must have a username.'))
        user = self.model(username=username, **extra_fields)
    else:  # Client
        if not phone_number:
            raise ValueError(_('Clients must have a phone number.'))
        user = self.model(phone_number=phone_number, **extra_fields)

    user.set_password(password)
    user.save(using=self._db)
    return user


def create_superuser_account(username, email=None, password=None, **extra_fields):
    return User.objects.create_superuser(username=username, email=email, password=password, **extra_fields)

