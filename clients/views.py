# views.py
from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound
from .services import get_all_clients, get_client_by_id, create_client, update_client, delete_client

def client_list(request):
    clients = get_all_clients()
    return render(request, 'clients/client_list.html', {'clients': clients})

def client_detail(request, client_id):
    client = get_client_by_id(client_id)
    if not client:
        return HttpResponseNotFound("Клиент не найден")
    return render(request, 'clients/client_detail.html', {'client': client})

def client_create(request):
    if request.method == 'POST':
        data = {
            'first_name': request.POST['first_name'],
            'primary_phone': request.POST['primary_phone'],
            'backup_phone': request.POST.get('backup_phone'),
            'company': request.POST.get('company'),
            'email': request.POST.get('email'),
        }
        create_client(data)
        return redirect('client_list')
    return render(request, 'clients/client_form.html')

def client_update(request, client_id):
    client = get_client_by_id(client_id)
    if not client:
        return HttpResponseNotFound("Клиент не найден")

    if request.method == 'POST':
        data = {
            'first_name': request.POST['first_name'],
            'primary_phone': request.POST['primary_phone'],
            'backup_phone': request.POST.get('backup_phone'),
            'company': request.POST.get('company'),
            'email': request.POST.get('email'),
        }
        update_client(client_id, data)
        return redirect('client_list')

    return render(request, 'clients/client_form.html', {'client': client})

def client_delete(request, client_id):
    if delete_client(client_id):
        return redirect('client_list')
    return HttpResponseNotFound("Клиент не найден")
