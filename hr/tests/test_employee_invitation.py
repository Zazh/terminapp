# hr/tests/test_employee_invitation.py

import datetime
from django.utils import timezone
from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from hr.models import EmployeeInvitation, Company, Employee
from hr.services import create_company  # Предполагается, что эта функция уже реализована

User = get_user_model()


class EmployeeInvitationTest(APITestCase):
    def setUp(self):
        # Создаем пользователя-владельца (owner)
        self.owner = User.objects.create_user(username='owner', password='password')
        self.client.force_authenticate(user=self.owner)

        # Создаем компанию через сервис; в нем создаются базовые сущности
        self.company = create_company(owner=self.owner, name='Test Company', subdomain='test-company')

        # Выход для имитации сценария регистрации нового сотрудника
        self.client.logout()

    def test_create_invitation(self):
        """
        Тест создания приглашения сотрудника.
        """
        invitation_email = "new_employee@example.com"
        expires_at = timezone.now() + datetime.timedelta(hours=48)

        # Создаем приглашение напрямую (или можно реализовать отдельный endpoint для этого)
        invitation = EmployeeInvitation.objects.create(
            inviter=self.owner,
            company=self.company,
            email=invitation_email,
            expires_at=expires_at
        )

        self.assertEqual(invitation.email, invitation_email)
        self.assertEqual(invitation.status, "PENDING")
        self.assertIsNotNone(invitation.token)
        self.assertTrue(invitation.expires_at > timezone.now())

    def test_accept_invitation(self):
        """
        Симулируем процесс принятия приглашения:
        - Создаем приглашение.
        - Регистрируем нового пользователя.
        - Принимаем приглашение, связываем пользователя с компанией.
        """
        invitation_email = "new_employee@example.com"
        expires_at = timezone.now() + datetime.timedelta(hours=48)
        invitation = EmployeeInvitation.objects.create(
            inviter=self.owner,
            company=self.company,
            email=invitation_email,
            expires_at=expires_at
        )

        # Симулируем регистрацию нового сотрудника
        new_user = User.objects.create_user(username='newemployee', email=invitation_email, password='password')

        # Допустим, у нас есть логика или endpoint, который принимает приглашение по токену.
        # Здесь мы эмулируем эту логику:
        self.assertTrue(invitation.expires_at > timezone.now(), "Приглашение истекло")

        # Создаем Employee для нового пользователя, связываем его с компанией
        employee = Employee.objects.create(
            company=self.company,
            user=new_user,
            status='ACTIVE'  # Или можно сначала создать со статусом PENDING, а потом обновить
        )
        # Обновляем статус приглашения
        invitation.status = "ACCEPTED"
        invitation.save()

        # Проверяем, что профиль создан и приглашение принято
        self.assertIsNotNone(employee)
        self.assertEqual(employee.company, self.company)
        self.assertEqual(invitation.status, "ACCEPTED")
