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
    # Пример вывода статуса «человеческим» языком
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    # Вложенный сериализатор EmployeeInfo (если нужно получать данные в одном запросе)
    info = EmployeeInfoSerializer(read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id',
            'user',       # Обычно PK, можно сделать PrimaryKeyRelatedField
            'role',
            'status',
            'status_display',
            'info',       # Вложенный read-only (пр. GET)
        ]

