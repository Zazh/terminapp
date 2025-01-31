# account/api.py

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import SessionAuthentication

from django.contrib.auth import login, logout
from django.contrib.auth import get_user_model

from .serializers import (
    RegistrationSerializer,
    LoginSerializer,
    UserSerializer
)
from .services import authenticate_user

User = get_user_model()


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    Если вы хотите тестировать через Postman, и возникает проблема CSRF,
    можно переопределить enforce_csrf().
    Но в продакшене обычно остаётся защита CSRF.
    """
    def enforce_csrf(self, request):
        return  # Отключаем CSRF для упрощённого тестирования, аккуратнее в продакшене.


class RegisterAPIView(generics.CreateAPIView):
    """
    Регистрация нового пользователя.
    """
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]
    authentication_classes = [CsrfExemptSessionAuthentication]

    def create(self, request, *args, **kwargs):
        """
        Переопределяем, чтобы сразу логинить пользователя после успешной регистрации
        (если нужно), и вернуть что-то, например serialized user data.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Логиним пользователя (Session-based)
        login(request, user, backend='account.authentication.EmailAuthBackend')

        # Возвращаем сериализованные данные
        user_data = UserSerializer(user).data
        return Response(user_data, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    """
    Логин через email+password, Session-based.
    """
    permission_classes = [AllowAny]
    authentication_classes = [CsrfExemptSessionAuthentication]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = authenticate_user(email, password)
        if user is None:
            return Response({"detail": "Invalid credentials"}, status=400)

        if not user.is_active:
            return Response({"detail": "User is inactive"}, status=400)

        # Django login (создаём sessionid cookie)
        login(request, user, backend='account.authentication.EmailAuthBackend')

        data = UserSerializer(user).data
        return Response(data, status=200)


class LogoutAPIView(APIView):
    """
    Выход из сессии.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    def post(self, request, *args, **kwargs):
        logout(request)
        return Response({"detail": "Logged out."}, status=200)


class ProfileAPIView(APIView):
    """
    Пример получения данных о текущем пользователе (Session-based).
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    def get(self, request, *args, **kwargs):
        user = request.user
        data = UserSerializer(user).data
        return Response(data, status=200)
