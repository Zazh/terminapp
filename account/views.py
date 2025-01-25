from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView

from .forms import ClientRegistrationForm, StaffRegistrationForm
from .services import create_client_user, create_staff_user


def register_client(request):
    """
    Регистрирует клиента (is_client=True) через телефон.
    """
    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone_number']
            password = form.cleaned_data['password1']  # поле из UserCreationForm
            user = create_client_user(phone_number=phone, password=password)
            login(request, user)
            messages.success(request, 'Client registration successful!')
            return redirect('profile')  # Или любая нужная страница
    else:
        form = ClientRegistrationForm()

    return render(request, 'account/register_client.html', {'form': form})


def register_staff(request):
    """
    Регистрирует сотрудника (is_staff=True) через email.
    """
    if request.method == 'POST':
        form = StaffRegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = create_staff_user(email=email, password=password, username=username)
            login(request, user)
            messages.success(request, 'Staff registration successful!')
            return redirect('profile')
    else:
        form = StaffRegistrationForm()

    return render(request, 'account/register_staff.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'account/login.html'


@login_required
def profile(request):
    return render(request, 'account/profile.html', {'user': request.user})