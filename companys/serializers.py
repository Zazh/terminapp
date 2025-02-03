# companys/serializers.py
from rest_framework import serializers
from .models import Company

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'subdomain', 'billing_plan', 'created_at']
        read_only_fields = ['id', 'billing_plan', 'created_at']

    def validate_subdomain(self, value):
        """
        Если subdomain передан, приводим его к нижнему регистру и убираем лишние пробелы.
        """
        if value:
            return value.lower().strip()
        return value

    def create(self, validated_data):
        # Получаем текущего пользователя из контекста
        request = self.context.get('request')
        owner = request.user if request else None
        if not owner:
            raise serializers.ValidationError("User must be authenticated to create a company.")
        from .services import create_company
        return create_company(
            owner=owner,
            name=validated_data.get('name'),
            subdomain=validated_data.get('subdomain'),
            billing_plan=validated_data.get('billing_plan', 'basic')
        )
