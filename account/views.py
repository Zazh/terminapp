# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.generic import FormView
from django.urls import reverse_lazy

from .forms import (
    ClientRegistrationForm,
    StaffRegistrationForm,
    CustomLoginForm
)
from .models import User
from .authentication import MultiIdentifierAuthBackend


def register_client(request):
    """Регистрация клиента через телефон (role=CLIENT)"""
    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='account.authentication.MultiIdentifierAuthBackend')
            messages.success(request, 'Регистрация клиента прошла успешно!')
            return redirect('profile')
    else:
        form = ClientRegistrationForm()

    return render(request, 'account/register_client.html', {'form': form})


def register_staff(request):
    """Регистрация сотрудника через email (role=STAFF)"""
    if request.method == 'POST':
        form = StaffRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'Регистрация сотрудника прошла успешно!')
            return redirect('profile')
    else:
        form = StaffRegistrationForm()

    return render(request, 'account/register_staff.html', {'form': form})


class CustomLoginView(FormView):
    """Кастомный вход с поддержкой email/телефона/username"""
    form_class = CustomLoginForm
    template_name = 'account/login.html'
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        identifier = form.cleaned_data['identifier']
        password = form.cleaned_data['password']

        user = MultiIdentifierAuthBackend().authenticate(
            self.request,
            identifier=identifier,
            password=password
        )

        if user:
            login(self.request, user)
            return super().form_valid(form)

        form.add_error(None, 'Неверные учетные данные')
        return self.form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['data'] = kwargs.get('data', {}).copy()
        if 'identifier' in kwargs['data']:
            kwargs['data']['username'] = kwargs['data'].pop('identifier')
        return kwargs


@login_required
def profile(request):
    """Профиль пользователя с учетом роли"""
    role_mapping = {
        User.Role.CLIENT: 'client',
        User.Role.STAFF: 'staff',
        User.Role.ADMIN: 'admin'
    }

    context = {
        'user': request.user,
        'role': role_mapping.get(request.user.role, 'unknown'),
        'is_client': request.user.is_client,
        'is_staff_member': request.user.is_staff,
    }

    return render(request, 'account/profile.html', context)