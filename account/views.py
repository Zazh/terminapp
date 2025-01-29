from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.generic import FormView
from django.urls import reverse_lazy
from account.authentication import EmailAuthBackend


from .forms import (
    UserRegistrationForm,  # можно базовую форму для клиента
    StaffRegistrationForm, # форму для сотрудника
    CustomLoginForm
)
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.contrib import messages

from django.contrib.auth import get_user_model

User = get_user_model()


def register_client(request):
    """
    Пример регистрации «клиента».
    Хотя в текущей модели User нет специальных полей,
    мы можем сохранить логику, если планируется дальнейшее развитие.
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Авторизуем сразу после регистрации
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'Регистрация прошла успешно (client)!')
            return redirect('profile')
    else:
        form = UserRegistrationForm()
    return render(request, 'account/register_client.html', {'form': form})


def register_staff(request):
    """
    Пример регистрации «сотрудника».
    Реально отличается, если StaffRegistrationForm собирает какие-то иные поля.
    """
    if request.method == 'POST':
        form = StaffRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Авторизуем сразу после регистрации
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'Регистрация прошла успешно (staff)!')
            return redirect('profile')
    else:
        form = StaffRegistrationForm()
    return render(request, 'account/register_staff.html', {'form': form})


class CustomLoginView(FormView):
    """
    Упрощённый вход с email + пароль.
    """
    form_class = CustomLoginForm
    template_name = 'account/login.html'
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']

        user = EmailAuthBackend().authenticate(
            self.request,
            email=email,
            password=password
        )

        if user:
            login(self.request, user)
            return super().form_valid(form)

        form.add_error(None, 'Неверные учетные данные')
        return self.form_invalid(form)



@login_required
def profile(request):
    """
    Пример профиля. Показываем только базовую информацию: email.
    Если нужно больше логики (roles, phone, и т.п.), выводите через отдельные модели профиля.
    """
    context = {
        'user': request.user,
        'is_staff_django': request.user.is_staff,  # флаг Django
    }
    return render(request, 'account/profile.html', context)


@receiver(user_logged_in)
def notify_login(sender, request, user, **kwargs):
    # Убираем ссылки на username или phone_number, которых больше нет
    messages.success(request, f'Welcome back, {user.email}!')
