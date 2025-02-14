from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .serializers import CompanySerializer
from .services import create_company

class CompanyCreateAPIView(generics.CreateAPIView):
    """
    API для создания компании.
    Доступ разрешён только авторизованным пользователям.
    """
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Вызываем сервисный слой для создания компании
        company = create_company(self.request.user, serializer.validated_data)
        return company