# clients/serializers.py
from rest_framework import serializers
from .models import Client

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = [
            'id',
            'first_name',
            'primary_phone',
            'backup_phone',
            'company',   # Отобразим в выводе, но редактировать запретим
            'email'
        ]
        # Запретим редактирование поля company на уровне сериализатора,
        # чтобы не менять компанию руками
        read_only_fields = ('company',)