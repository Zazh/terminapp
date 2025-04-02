# hr/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from hr.api import CompanyViewSet, EmployeeInvitationViewSet, InvitationAcceptAPIView

router = DefaultRouter()
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'invitations', EmployeeInvitationViewSet, basename='employee-invitation')

urlpatterns = [
    path('invitations/accept/', InvitationAcceptAPIView.as_view(), name='invitation-accept'),
    path('', include(router.urls)),
]
