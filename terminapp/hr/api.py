# hr/api.py
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from hr.serializers import CompanySerializer, EmployeeInvitationCreateSerializer, InvitationAcceptSerializer
from hr.models import EmployeeInvitation
from hr.services import create_company

class CompanyViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        serializer = CompanySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            company = create_company(
                owner=request.user,
                name=serializer.validated_data['name'],
                subdomain=serializer.validated_data['subdomain'],
                billing_plan=serializer.validated_data.get('billing_plan', 'BASE')
            )
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        output_serializer = CompanySerializer(company)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class EmployeeInvitationViewSet(viewsets.ModelViewSet):
    """
    API для создания и просмотра приглашений сотрудников.
    При создании приглашения автоматически устанавливаются inviter и company.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeInvitationCreateSerializer

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'employee_profile'):
            company = user.employee_profile.company
            return EmployeeInvitation.objects.filter(company=company)
        return EmployeeInvitation.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        company = user.employee_profile.company
        # Сохраняем приглашение, связывая его с текущим пользователем и компанией
        serializer.save(inviter=user, company=company)


@method_decorator(csrf_exempt, name='dispatch')
class InvitationAcceptAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = InvitationAcceptSerializer

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        data = request.data.dict()
        if 'token' not in data and 'token' in request.query_params:
            data['token'] = request.query_params['token']

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "detail": "Registration successful!",
                "email": user.email,
                "id": user.id
            },
            status=status.HTTP_201_CREATED
        )

    def get_authentication_classes(self):
        return []

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if 'token' in self.request.query_params:
            context['token'] = self.request.query_params['token']
        return context