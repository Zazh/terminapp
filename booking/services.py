from datetime import datetime
from django.db import transaction
from .models import Booking, BookingItem, BookingStatus, BookingItemStatus
from orders.models import Order

@transaction.atomic
def create_booking(
    order: Order,
    start_dt: datetime,
    end_dt: datetime,
    items_with_qty_and_status=None
):
    """
    Создать бронирование для указанного заказа на период [start_dt - end_dt].
    :param items_with_qty_and_status: может быть списком словарей вида:
      [
         {
           'order_item_id': 10,
           'quantity': 3,
           'status': 'confirmed',        # если нужно сразу поставить
           'start_datetime': ...,
           'end_datetime': ...
         },
         ...
      ]
      Если None или пусто, то бронируем все позиции (quantity = order_item.quantity), статус = pending и наследуем даты.
    """
    booking = Booking.objects.create(
        order=order,
        start_datetime=start_dt,
        end_datetime=end_dt,
        status=BookingStatus.PENDING
    )

    if items_with_qty_and_status:
        for item_data in items_with_qty_and_status:
            BookingItem.objects.create(
                booking=booking,
                order_item_id=item_data['order_item_id'],
                quantity=item_data.get('quantity', 1),
                status=item_data.get('status', BookingItemStatus.PENDING),
                start_datetime=item_data.get('start_datetime'),
                end_datetime=item_data.get('end_datetime'),
            )
    else:
        # Если ничего не передано – бронируем все OrderItem
        for oi in order.order_items.all():
            BookingItem.objects.create(
                booking=booking,
                order_item=oi,
                quantity=oi.quantity,
                status=BookingItemStatus.PENDING,
                # даты не указываем => будут наследоваться от booking
            )

    # После создания всех BookingItem'ов вызываем пересчёт статуса (вдруг что-то поменяется)
    booking.recalc_status_from_items()
    return booking

@transaction.atomic
def update_booking_status(booking: Booking, new_status: str):
    """
    Пример принудительной установки статуса бронирования (если это вообще нужно).
    Однако, помните, что booking сам "затащит" себе минимальный статус из items.
    """
    # Здесь можно добавить логику проверки допустимых переходов
    booking.status = new_status
    booking.save()
    return booking