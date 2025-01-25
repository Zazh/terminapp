from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class ClientRegistrationForm(UserCreationForm):
    phone_number = forms.CharField(max_length=15, required=True, label="Phone Number")

    class Meta:
        model = User
        fields = ('phone_number',)  # плюс поля паролей (password1, password2) идут от UserCreationForm


class StaffRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = User
        fields = ('username', 'email')  # плюс password1, password2