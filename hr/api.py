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
    link_with_token = None  # атрибут класса

    def get_queryset(self):
        user = self.request.user
        # Предполагается, что у пользователя есть связь с компанией через Employee профиль.
        if hasattr(user, 'employee_profile'):
            company = user.employee_profile.company
            return EmployeeInvitation.objects.filter(company=company)
        return EmployeeInvitation.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        company = user.employee_profile.company

        # Создаём приглашение один раз
        invitation = serializer.save(inviter=user, company=company)

        accept_url = self.request.build_absolute_uri(reverse('invitation-accept'))
        link_with_token = f"{accept_url}?token={invitation.token}"
        self.link_with_token = link_with_token

    def create(self, request, *args, **kwargs):
        """ Переопределим create, чтобы кроме сериализованных данных вернуть ссылку. """
        response = super().create(request, *args, **kwargs)
        # У нас в perform_create сохранена ссылка self.link_with_token
        if hasattr(self, 'link_with_token'):
            # Добавляем ссылку в ответ
            response.data['invitation_link'] = self.link_with_token
        return response


@method_decorator(csrf_exempt, name='dispatch')
class InvitationAcceptAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = InvitationAcceptSerializer

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        Переопределяем метод create, чтобы вернуть свой ответ
        """
        # Попробуем достать token из query_params, если нет в теле
        data = dict(request.data)
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
        # Полностью отключаем аутентификацию для этого эндпоинта
        return []

    def get_serializer_context(self):
        """
        В context можно передать query-параметры, чтобы внутри
        InvitationAcceptSerializer их забрать
        """
        context = super().get_serializer_context()
        if 'token' in self.request.query_params:
            context['token'] = self.request.query_params['token']
        return context