# account/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import User


class UserRegistrationForm(UserCreationForm):
    """Общая форма регистрации, только email + пароль."""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'name@example.com'})
    )

    class Meta:
        model = User
        fields = ('email',)

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError(_("This email is already registered."))
        return email


class StaffRegistrationForm(UserCreationForm):
    """
    Пример отдельной формы для «сотрудника».
    Можно добавить поля специфичные для сотрудника,
    хотя сейчас они идентичны.
    """
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('email',)

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError(_("This email is already registered."))
        return email


class CustomLoginForm(forms.Form):
    """
    Упростили форму логина: теперь только email + password,
    раз phone_number и username не используются.
    """
    email = forms.EmailField(label=_("Email"))
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
