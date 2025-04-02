from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
# from django.utils.timezone import now

from orders.models import Order, OrderItem


class BookingStatus(models.TextChoices):
    """
    Статусы для самого Booking.
    При создании берём PENDING (в процессе).
    """
    PENDING = 'pending', _('В процессе')
    CONFIRMED = 'confirmed', _('Подтверждено')
    COMPLETED = 'completed', _('Завершено')
    CANCELLED = 'cancelled', _('Отменено')


class BookingItemStatus(models.TextChoices):
    """
    Статусы для отдельных позиций брони (BookingItem).
    """
    PENDING = 'pending', _('В процессе')
    CONFIRMED = 'confirmed', _('Подтверждено')
    COMPLETED = 'completed', _('Завершено')
    CANCELLED = 'cancelled', _('Отменено')
    # Если нужна логика переноса/пересcheduling – можно добавить:
    # RESCHEDULED = 'rescheduled', _('Перенесён')


class Booking(models.Model):
    """
    Главная модель "Бронирование" (на один заказ).
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name="Заказ"
    )

    # Начало и конец брони (дата/время)
    start_datetime = models.DateTimeField(
        verbose_name="Начало брони",
        null = True,  # Временно разрешаем NULL2
        blank = True,  # Необязательное поле в формах
    )
    end_datetime = models.DateTimeField(
        verbose_name="Конец брони",
        null=True,  # Временно разрешаем NULL
        blank=True,  # Необязательное поле в формах
    )

    status = models.CharField(
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING,
        verbose_name="Статус брони"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Бронь #{self.pk} [Заказ №{self.order_id}]"

    @property
    def client(self):
        """Возвращаем клиента через связанный заказ."""
        return self.order.client

    def recalc_status_from_items(self):
        """
        Пересчитывает статус бронирования, исходя из "минимального" статуса среди booking_items.
        Правила:
          - Статусы ранжируются так: pending (0) < confirmed (1) < completed (2) < cancelled (3).
          - Если у одного из items статус 'pending', то booking станет 'pending' и т.д.
          - Если все completed, то booking = completed,
          - Если есть хотя бы один cancelled, booking = cancelled,
          - и т.д.

        Вы можете адаптировать логику под ваши нужды.
        """
        # Считываем все статусы позиций
        item_statuses = self.booking_items.values_list('status', flat=True)

        # Если у бронирования нет позиций (редкий случай) - оставим текущий
        if not item_statuses:
            return

        # Определяем числовые ранги для статусов:
        rank_map = {
            BookingItemStatus.PENDING: 0,
            BookingItemStatus.CONFIRMED: 1,
            BookingItemStatus.COMPLETED: 2,
            BookingItemStatus.CANCELLED: 3,
        }

        # Ищем минимальный ранг
        min_rank = None
        for st in item_statuses:
            r = rank_map[st]
            if min_rank is None or r < min_rank:
                min_rank = r

        # Обратный словарь для статусов (min_rank -> BookingStatus)
        # По умолчанию сделаем прямое соответствие:
        #   0 -> pending
        #   1 -> confirmed
        #   2 -> completed
        #   3 -> cancelled
        # Если нужен другой маппинг — скорректируйте.
        inverse_map = {
            0: BookingStatus.PENDING,
            1: BookingStatus.CONFIRMED,
            2: BookingStatus.COMPLETED,
            3: BookingStatus.CANCELLED,
        }

        new_status = inverse_map[min_rank]

        if self.status != new_status:
            self.status = new_status
            self.save()


class BookingItem(models.Model):
    """
    Детализация бронирования (конкретные позиции из заказа).
    """
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='booking_items',
        verbose_name="Бронирование"
    )
    order_item = models.ForeignKey(
        OrderItem,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name="Позиция заказа"
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="Забронированное количество"
    )

    # При желании – свои собственные даты/время
    start_datetime = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Начало брони (элемент)"
    )
    end_datetime = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Конец брони (элемент)"
    )

    # Статус конкретной позиции брони
    status = models.CharField(
        max_length=20,
        choices=BookingItemStatus.choices,
        default=BookingItemStatus.PENDING,
        verbose_name="Статус позиции"
    )

    class Meta:
        verbose_name = "Позиция бронирования"
        verbose_name_plural = "Позиции бронирования"

    def __str__(self):
        return f"BookingItem #{self.pk} | Booking #{self.booking_id}"

    @property
    def effective_start_datetime(self):
        """
        Если нет своего start_datetime, возвращаем start_datetime родительского бронирования.
        """
        if self.start_datetime:
            return self.start_datetime
        return self.booking.start_datetime

    @property
    def effective_end_datetime(self):
        """
        Если нет своего end_datetime, возвращаем end_datetime родительского бронирования.
        """
        if self.end_datetime:
            return self.end_datetime
        return self.booking.end_datetime

    def save(self, *args, **kwargs):
        """
        Переопределяем save, чтобы после сохранения автоматически пересчитывать статус
        в родительском Booking (с учётом «lowest» статуса).
        """
        super().save(*args, **kwargs)
        self.booking.recalc_status_from_items()


@receiver(post_save, sender=BookingItem)
def update_booking_status_on_item_save(sender, instance, **kwargs):
    """
    На случай, если мы хотим быть уверены, что при каждом сохранении BookingItem
    статус Booking пересчитывается.
    """
    instance.booking.recalc_status_from_items()