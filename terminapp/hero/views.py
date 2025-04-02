# hero/views.py

from django.http import HttpResponse

def main_placeholder(request):
    return HttpResponse("<h1>Главная страница сервиса (заглушка)</h1>")
