# account/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import gettext_lazy as _
from .models import User


class CustomUserCreationForm(forms.ModelForm):
    """
    Форма для создания нового пользователя через админку.
    """
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'is_staff', 'is_active',)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("Passwords don't match."))
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class CustomUserChangeForm(forms.ModelForm):
    """
    Форма редактирования пользователя в админке (read-only пароль).
    """
    password = ReadOnlyPasswordHashField(
        label=_("Password"),
        help_text=_("Raw passwords are not stored, so there is no way to see "
                    "this user's password, but you can change the password "
                    "using <a href=\"password/\">this form</a>.")
    )

    class Meta:
        model = User
        fields = ('email', 'is_staff', 'is_superuser', 'is_active', 'password')

    def clean_password(self):
        return self.initial["password"]


class CustomUserAdmin(UserAdmin):
    """
    Настройки отображения модели User в админке.
    """
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    model = User

    list_display = ('email', 'is_staff', 'is_active', 'date_joined')  # ✅ Здесь можно оставить    list_filter = ('is_staff', 'is_active')
    search_fields = ('email',)
    ordering = ('email',)

    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        (_("Permissions"), {
            'fields': (
                'is_staff',
                'is_superuser',
                'is_active',
                'groups',
                'user_permissions',
            )
        }),
        (_("Important dates"), {
            'fields': ('last_login',)
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'is_staff',
                'is_superuser',
                'is_active'
            )
        }),
    )


admin.site.register(User, CustomUserAdmin)
