# services.py
from .models import Client

def get_all_clients():
    print("Получение всех клиентов")
    return Client.objects.all()

def get_client_by_id(client_id):
    print(f"Получение клиента с ID: {client_id}")
    return Client.objects.filter(id=client_id).first()

def create_client(data):
    print(f"Создание клиента с данными: {data}")
    client = Client(**data)
    client.save()
    return client

def update_client(client_id, data):
    print(f"Обновление клиента с ID {client_id}, данные: {data}")
    client = get_client_by_id(client_id)
    if client:
        for field, value in data.items():
            setattr(client, field, value)
        client.save()
        return client
    return None

def delete_client(client_id):
    print(f"Удаление клиента с ID: {client_id}")
    client = get_client_by_id(client_id)
    if client:
        client.delete()
        return True
    return False