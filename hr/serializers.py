# hr/serializers.py
from rest_framework import serializers
from hr.models import Company, EmployeeInvitation, Employee
from django.contrib.auth import get_user_model
from django.utils import timezone
import datetime

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('id', 'name', 'subdomain', 'billing_plan', 'created_at')
        read_only_fields = ('id', 'created_at')


class EmployeeInvitationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeInvitation
        fields = ('id', 'email', 'token', 'status', 'created_at', 'expires_at')
        read_only_fields = ('id', 'token', 'status', 'created_at', 'expires_at')

    def create(self, validated_data):
        # Автоматически устанавливаем срок действия приглашения (например, 48 часов)
        validated_data['expires_at'] = timezone.now() + datetime.timedelta(hours=48)
        return super().create(validated_data)


User = get_user_model()

class InvitationAcceptSerializer(serializers.Serializer):
    token = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        token = data.get('token')
        try:
            invitation = EmployeeInvitation.objects.get(token=token, status='PENDING')
        except EmployeeInvitation.DoesNotExist:
            raise serializers.ValidationError("Неверный или недействительный токен приглашения.")

        if invitation.expires_at < timezone.now():
            raise serializers.ValidationError("Срок действия приглашения истёк.")

        data['invitation'] = invitation
        return data


    def create(self, validated_data):
        invitation = validated_data['invitation']
        password = validated_data['password']
        # username = validated_data.get('username') or invitation.email

        # Проверяем, существует ли пользователь с таким email
        if User.objects.filter(email=invitation.email).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует.")

        # Создаем пользователя
        user = User.objects.create_user(email=invitation.email, password=password)

        # Создаем профиль сотрудника, связывая его с компанией из приглашения
        Employee.objects.create(
            company=invitation.company,
            user=user,
            status='ACTIVE'
        )

        # Помечаем приглашение как принятое
        invitation.status = "ACCEPTED"
        invitation.save()

        return user