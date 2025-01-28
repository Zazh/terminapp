from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _  # Добавить этот импорт
from .models import User
import re


class ClientRegistrationForm(UserCreationForm):
    phone_number = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': '+1234567890'})
    )

    class Meta:
        model = User
        fields = ('phone_number',)

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if not re.match(r'^\+?1?\d{9,15}$', phone_number):
            raise ValidationError(_("Invalid phone number format"))

        if User.objects.filter(phone_number=phone_number).exists():
            raise ValidationError(_("Phone number already registered"))

        return phone_number

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.CLIENT
        if commit:
            user.save()
        return user


class StaffRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'name@company.com'})
    )

    class Meta:
        model = User
        fields = ('email', 'username')

    def clean_email(self):
        email = self.cleaned_data['email']
        if not email.endswith('@company.com'):
            raise ValidationError(_("Only company emails allowed"))

        if User.objects.filter(email=email).exists():
            raise ValidationError(_("Email already registered"))

        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.STAFF
        if commit:
            user.save()
        return user

class CustomLoginForm(forms.Form):
    identifier = forms.CharField(label="Email/Phone/Username")
    password = forms.CharField(widget=forms.PasswordInput)