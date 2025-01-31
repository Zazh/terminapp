# account/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class RegistrationSerializer(serializers.Serializer):
    """
    Сериализатор регистрации:
    - email
    - password
    - password2 (подтверждение)
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs

    def create(self, validated_data):
        """
        Метод create() вызывается DRF при serializer.save().
        Здесь фактически создаём пользователя через сервис.
        """
        from account.services import create_new_user

        email = validated_data['email']
        password = validated_data['password']
        # Удаляем password2 — он нам больше не нужен
        validated_data.pop('password2', None)

        # Можно добавить любые extra_fields
        user = create_new_user(email=email, password=password)
        return user


class LoginSerializer(serializers.Serializer):
    """
    Сериализатор логина по email + пароль.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    """
    Для вывода инфо о текущем пользователе.
    """
    class Meta:
        model = User
        fields = ['id', 'email', 'is_staff', 'is_active', 'date_joined']
