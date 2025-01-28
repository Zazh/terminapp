# authentication.py
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from .models import User


class MultiIdentifierAuthBackend(ModelBackend):
    def authenticate(self, request, identifier=None, password=None, **kwargs):
        try:
            user = User.objects.get(
                Q(email=identifier) |
                Q(phone_number=identifier) |
                Q(username=identifier)
            )

            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            return None