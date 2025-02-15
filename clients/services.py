# clients/services.py
from .models import Client

def get_all_clients():
    return Client.objects.all()

def get_client_by_id(client_id):
    return Client.objects.filter(id=client_id).first()

def create_client(company, data):
    """
    Принимаем объект Company вместо company_name (строки).
    """
    data['company'] = company
    client = Client(**data)
    client.save()
    return client

def update_client(client_id, company, data):
    client = get_client_by_id(client_id)
    if not client:
        return None
    # Принудительно выставляем нужную компанию
    data['company'] = company
    for field, value in data.items():
        setattr(client, field, value)
    client.save()
    return client

def delete_client(client_id, company):
    client = get_client_by_id(client_id)
    # Проверяем, принадлежит ли клиент указанной компании
    if client and client.company == company:
        client.delete()
        return True
    return False