import random
from decimal import Decimal
from faker import Faker
from orders.models import Order, OrderItem
from products.models import Product
from clients.models import Client

fake = Faker()

def generate_test_data():
    # Создаём тестового клиента
    client = Client.objects.create(
        first_name=fake.first_name(),
        email=fake.email(),
        primary_phone=fake.phone_number()
    )
    print(f"Создан клиент: {client}")

    # Создаём несколько продуктов
    products = [
        Product.objects.create(
            name=fake.word(),
            price=Decimal(random.uniform(10, 100)).quantize(Decimal("0.01"))
        )
        for _ in range(5)
    ]
    print(f"Создано продуктов: {len(products)}")

    # Создаём заказ
    order = Order.objects.create(
        client=client,
        status='pending',
        total_amount=Decimal("0.00")
    )
    print(f"Создан заказ: {order}")

    # Добавляем позиции к заказу
    for product in products:
        quantity = random.randint(1, 5)
        price = product.price
        discount = Decimal(random.uniform(0, price / 2)).quantize(Decimal("0.01"))
        order_item = OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=price,
            discount=discount,
            status='pending'
        )
        print(f"Добавлена позиция: {order_item}")

    # Пересчитываем сумму заказа
    order.total_amount = sum([item.calculate_amount() for item in order.order_items.all()])
    order.save()
    print(f"Итоговая сумма заказа: {order.total_amount}")

if __name__ == "__main__":
    generate_test_data()
