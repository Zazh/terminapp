# api.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from hr.models import CompanyMixin
from .models import Order, OrderItem, OrderItemRefund
from .serializers import OrderSerializer, OrderItemSerializer, OrderItemRefundSerializer
from .services import OrderService, OrderItemService

class OrderViewSet(CompanyMixin, viewsets.ModelViewSet):
    """
    CRUD для заказов.
    """
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(company=self.request.user.company)

    def create(self, request, *args, **kwargs):
        """
        Переопределяем create, чтобы использовать OrderService.
        """
        client_id = request.data.get('client')
        # Можно добавить и другие поля — например, если нужно что-то ещё при создании

        order = OrderService.create_order(
            client_id=client_id,
            company=request.user.company  # Автоматически изолируем данные
        )
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        Полное обновление Order (PUT).
        """
        partial = False
        return self._update_order(request, partial=partial)

    def partial_update(self, request, *args, **kwargs):
        """
        Частичное обновление Order (PATCH).
        """
        partial = True
        return self._update_order(request, partial=partial)

    def _update_order(self, request, partial):
        order = self.get_object()
        # Собираем поля, которые разрешено обновлять:
        update_data = {}
        for field in ['client', 'status']:
            if field in request.data:
                update_data[field] = request.data[field]

        updated_order = OrderService.update_order(order_id=order.id, **update_data)
        serializer = self.get_serializer(updated_order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        order = self.get_object()
        OrderService.delete_order(order.id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderItemViewSet(viewsets.ModelViewSet):
    """
    CRUD для позиций заказа.
    """
    permission_classes = [IsAuthenticated]
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

    def get_queryset(self):
        return OrderItem.objects.filter(company=self.request.user.company)

    def create(self, request, *args, **kwargs):
        """
        Создание позиции в заказе через OrderItemService.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated = serializer.validated_data
        order_id = validated['order'].id
        product_id = validated['product'].id
        quantity = validated['quantity']
        price = validated.get('price')  # может быть None
        discount = validated.get('discount', 0)
        wallet = validated.get('wallet')
        status_item = validated.get('status', 'pending')

        order_item = OrderItemService.create_order_item(
            order_id=order_id,
            product_id=product_id,
            quantity=quantity,
            price=price,
            discount=discount,
            wallet_id=wallet.id if wallet else None,
            status=status_item
        )
        out_serializer = self.get_serializer(order_item)
        return Response(out_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        Полное обновление (PUT) конкретной позиции.
        """
        partial = False
        return self._update_order_item(request, partial=partial)

    def partial_update(self, request, *args, **kwargs):
        """
        Частичное обновление (PATCH).
        """
        partial = True
        return self._update_order_item(request, partial=partial)

    def _update_order_item(self, request, partial):
        order_item = self.get_object()
        serializer = self.get_serializer(order_item, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        validated = serializer.validated_data
        update_fields = {}
        # Собираем те поля, которые хотим разрешить менять
        for field in ['quantity', 'price', 'discount', 'wallet', 'status']:
            if field in validated:
                value = validated[field]
                # Если wallet=None, нужно передавать None
                if field == 'wallet':
                    update_fields['wallet_id'] = value.id if value else None
                else:
                    update_fields[field] = value

        updated_item = OrderItemService.update_order_item(
            order_item_id=order_item.id,
            **update_fields
        )
        out_serializer = self.get_serializer(updated_item)
        return Response(out_serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        order_item = self.get_object()
        OrderItemService.delete_order_item(order_item.id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderItemRefundViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return OrderItem.objects.filter(company=self.request.user.company)

    permission_classes = [IsAuthenticated]
    queryset = OrderItemRefund.objects.all()
    serializer_class = OrderItemRefundSerializer

