# orders/views.py
from django.views.generic import ListView, DetailView, CreateView, FormView, TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.db import transaction
from django.db.models import Q
from clients.models import Client

from .models import Order, OrderItem, OrderItemRefund
from .forms import OrderForm, OrderItemForm, OrderItemRefundForm, RefundSearchForm
from .services import recalc_order_total


class OrderListView(ListView):
    model = Order
    template_name = 'orders/orders_list.html'
    context_object_name = 'object_list'
    # paginate_by = 10  # при необходимости можно включить пагинацию


class OrderDetailView(DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'object'

    # Можно переопределить get_context_data, если надо добавить доп. данные


class OrderCreateView(CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_form.html'
    success_url = reverse_lazy('orders:order_list')  # После создания - возвращаемся к списку

    def form_valid(self, form):
        """Если нужно что-то сделать с заказом сразу после сохранения"""
        response = super().form_valid(form)
        # Например, пересчитать total_amount (но там скорее всего 0)
        return response


class OrderItemCreateView(CreateView):
    model = OrderItem
    form_class = OrderItemForm
    template_name = 'orders/order_item_form.html'

    def get_success_url(self):
        # после добавления позиции вернёмся на страницу детального просмотра
        order_id = self.kwargs.get('order_id')
        return reverse_lazy('orders:order_detail', kwargs={'pk': order_id})

    def form_valid(self, form):
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, pk=order_id)

        # Создаём позицию, но пока не сохраняем окончательно (commit=False)
        order_item = form.save(commit=False)
        order_item.order = order  # привязываем к конкретному заказу
        # можно в order_item.status задать нужный статус, если требуется.
        order_item.save()  # теперь сохраняем

        # Пересчитываем сумму заказа после добавления позиции
        recalc_order_total(order)

        return super().form_valid(form)


# orders/views.py
class OrderRefundView(CreateView):
    model = OrderItemRefund
    form_class = OrderItemRefundForm
    template_name = 'orders/order_refund.html'

    def get_form_kwargs(self):
        """
        Переопределяем kwargs формы, чтобы сразу записать order_item
        в instance ещё до валидации (form.is_valid()).
        """
        kwargs = super().get_form_kwargs()
        order_item_id = self.kwargs['order_item_id']
        order_item = get_object_or_404(OrderItem, pk=order_item_id)

        # Если уже есть instance (редко бывает в CreateView), модифицируем его:
        instance = kwargs.get('instance', None)
        if instance is None:
            # Создаём новый объект, указывая сразу order_item:
            instance = OrderItemRefund(order_item=order_item)
        else:
            # Если по каким-то причинам instance уже есть, проставляем order_item
            instance.order_item = order_item

        kwargs['instance'] = instance
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_item = get_object_or_404(OrderItem, pk=self.kwargs['order_item_id'])
        context['order_item'] = order_item
        return context

    def form_valid(self, form):
        """
        Так как order_item мы уже присвоили в get_form_kwargs,
        здесь можем просто сохранить объект и выполнить доп. логику.
        """
        refund = form.save(commit=False)
        order_item = refund.order_item  # Уже доступно
        refund.save()

        # Допустим, если полностью возвращаем, отменяем позицию
        if refund.refund_quantity == order_item.quantity:
            order_item.status = 'cancelled'
            order_item.save()

        # Пересчёт total_amount
        recalc_order_total(order_item.order)

        # Редирект обратно в детали заказа
        return redirect('orders:order_detail', pk=order_item.order.id)

@transaction.atomic
def order_item_cancel(request, item_id):
    """
    Функция для отмены (изменения статуса) позиции заказа.
    Допустим, ставим статус 'cancelled'.
    """
    item = get_object_or_404(OrderItem, pk=item_id)
    # Можем проверить логику (например, если уже оплачен, то другая логика, и т.д.)
    item.status = 'cancelled'
    item.save()

    # Пересчитываем сумму заказа (если отменили — нужно скорректировать total_amount)
    recalc_order_total(item.order)

    return redirect('orders:order_detail', pk=item.order_id)

class RefundSearchView(FormView):
    template_name = 'orders/refund_search.html'
    form_class = RefundSearchForm

    def form_valid(self, form):
        """
        Если форма валидна, ищем клиента по основному или резервному телефону.
        """
        phone = form.cleaned_data['phone']
        try:
            client = Client.objects.get(Q(primary_phone=phone) | Q(backup_phone=phone))
        except Client.DoesNotExist:
            form.add_error('phone', "Клиент с таким телефоном не найден.")
            return self.form_invalid(form)

        # Перенаправляем на список заказов клиента
        return redirect(reverse('orders:refund_orders_list') + f'?client_id={client.id}')


class RefundOrdersListView(TemplateView):
    template_name = 'orders/refund_orders_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client_id = self.request.GET.get('client_id')
        client = get_object_or_404(Client, pk=client_id)
        orders = Order.objects.filter(client=client)

        context['client'] = client
        context['orders'] = orders
        return context

class RefundOrderItemsView(TemplateView):
    template_name = 'orders/refund_order_items.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = kwargs.get('order_id')
        order = get_object_or_404(Order, pk=order_id)
        order_items = order.order_items.all()

        context['order'] = order
        context['order_items'] = order_items
        return context