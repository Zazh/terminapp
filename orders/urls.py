# orders/urls.py
from django.urls import path
from . import views
from .views import (
    OrderRefundView,
    RefundSearchView,
    RefundOrdersListView,
    RefundOrderItemsView
)

app_name = 'orders'

urlpatterns = [
    # 1) Список заказов
    path('', views.OrderListView.as_view(), name='order_list'),

    # 2) Создание нового заказа
    path('create/', views.OrderCreateView.as_view(), name='order_create'),

    # 3) Детальный просмотр заказа
    path('<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),

    # 4) Добавление позиции к заказу
    path('<int:order_id>/add-item/', views.OrderItemCreateView.as_view(), name='order_item_add'),

    # 5) Отмена (изменение статуса) позиции заказа
    path('item/<int:item_id>/cancel/', views.order_item_cancel, name='order_item_cancel'),

    # 6) Возврат средств
    path('item/<int:order_item_id>/refund/', OrderRefundView.as_view(), name='order_refund'),

    # 1) Форма поиска клиента
    path('refund/search/', RefundSearchView.as_view(), name='refund_search'),

    # 2) Список заказов клиента
    path('refund/orders/', RefundOrdersListView.as_view(), name='refund_orders_list'),

    # 3) Список позиций заказа
    path('refund/order-items/<int:order_id>/', RefundOrderItemsView.as_view(), name='refund_order_items'),

]