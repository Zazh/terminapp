# hr/serializers.py
from django.urls import reverse
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
    # Вычисляемое поле для формирования ссылки приглашения
    invitation_link = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeInvitation
        # Поле token исключено из возвращаемых данных
        fields = ('id', 'email', 'invitation_link', 'status', 'created_at', 'expires_at')
        read_only_fields = ('id', 'invitation_link', 'status', 'created_at', 'expires_at')

    def get_invitation_link(self, obj):
        request = self.context.get('request')
        # Генерируем URL для активации приглашения (предполагается, что URL с именем 'invitation-accept' настроен в urls.py)
        accept_url = request.build_absolute_uri(reverse('invitation-accept'))
        return f"{accept_url}?token={obj.token}"

    def create(self, validated_data):
        # Устанавливаем срок действия приглашения (48 часов)
        validated_data['expires_at'] = timezone.now() + datetime.timedelta(hours=48)
        return super().create(validated_data)

User = get_user_model()

class InvitationAcceptSerializer(serializers.Serializer):
    token = serializers.CharField(write_only=True, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        # Если токен не указан в data, попробуем взять его из контекста
        if 'token' not in data or not data['token']:
            token_from_context = self.context.get('token')
            if token_from_context:
                data['token'] = token_from_context
        token = data.get('token')
        if not token:
            raise serializers.ValidationError({"token": "Это поле обязательно."})

        try:
            invitation = EmployeeInvitation.objects.get(token=token, status='PENDING')
        except EmployeeInvitation.DoesNotExist:
            raise serializers.ValidationError({"token": "Неверный или недействительный токен приглашения."})

        if invitation.expires_at < timezone.now():
            raise serializers.ValidationError({"token": "Срок действия приглашения истёк."})

        data['invitation'] = invitation
        return data

    def create(self, validated_data):
        invitation = validated_data['invitation']
        password = validated_data['password']

        # Проверяем, существует ли пользователь с таким email
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if User.objects.filter(email=invitation.email).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует.")

        # Создаем пользователя
        user = User.objects.create_user(email=invitation.email, password=password)

        # Создаем профиль сотрудника, связывая его с компанией из приглашения
        from hr.models import Employee
        Employee.objects.create(
            company=invitation.company,
            user=user,
            status='ACTIVE'
        )

        # Помечаем приглашение как принятое
        invitation.status = "ACCEPTED"
        invitation.save()

        return user