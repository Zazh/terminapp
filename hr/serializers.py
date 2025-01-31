# hr/serializers.py

from rest_framework import serializers
from .models import (
    Department,
    Role,
    Employee,
    EmployeeInfo,
)

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class EmployeeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeInfo
        fields = '__all__'


class EmployeeSerializer(serializers.ModelSerializer):
    """
    Сериализатор сотрудника.
    - Выводим status_display (текстовое значение статуса).
    - Вкладываем info (read-only), чтобы одним запросом получать данные EmployeeInfo.
    - Вместо role теперь делаем roles (ManyToMany).
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    info = EmployeeInfoSerializer(read_only=True)

    # Пример: если хотим давать возможность управлять ролями по ID:
    roles = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Role.objects.all()
    )

    class Meta:
        model = Employee
        fields = [
            'id',
            'company',      # Если хотим видеть/управлять company здесь (не всегда безопасно)
            'user',         # PK: можно скрыть или сделать read_only, по вашему выбору
            'roles',        # Замена поля 'role' → 'roles' (M2M)
            'status',
            'status_display',
            'info',
        ]
