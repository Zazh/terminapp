# clients/api.py
from django.db import IntegrityError
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import ClientSerializer
from . import services

class ClientViewSet(viewsets.ModelViewSet):
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Фильтруем клиентов по текущей компании пользователя.
        Теперь сравниваем не строки, а объекты ForeignKey.
        """
        user_company = self.request.user.employee_profile.company
        return services.get_all_clients().filter(company=user_company)

    def create(self, request, *args, **kwargs):
        """
        Ловим IntegrityError, чтобы вернуть понятное сообщение
        при дубликате (company, primary_phone).
        """
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError as e:
            if 'unique_phone_within_company' in str(e):
                return Response(
                    {"detail": "Клиент с таким номером телефона уже существует в вашей компании."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            raise e

    def perform_create(self, serializer):
        user_company = self.request.user.employee_profile.company
        data = serializer.validated_data
        client = services.create_client(user_company, data)
        serializer.instance = client

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except IntegrityError as e:
            if 'unique_phone_within_company' in str(e):
                return Response(
                    {"detail": "Клиент с таким номером телефона уже существует в вашей компании."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            raise e

    def perform_update(self, serializer):
        user_company = self.request.user.employee_profile.company
        instance = serializer.instance
        data = serializer.validated_data
        updated_client = services.update_client(instance.id, user_company, data)
        serializer.instance = updated_client

    def destroy(self, request, *args, **kwargs):
        user_company = self.request.user.employee_profile.company
        client_id = kwargs.get('pk')
        success = services.delete_client(client_id, user_company)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"detail": "Не найдено или нет прав на удаление."},
            status=status.HTTP_404_NOT_FOUND
        )