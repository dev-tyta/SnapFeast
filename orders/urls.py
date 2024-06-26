from django.urls import path

from .views import OrderList, OrderDetail, CreateOrderView


urlpatterns = [
    path("create/", CreateOrderView.as_view(), name="create_order"),
    path("<int:pk>/", OrderDetail.as_view(), name="order_details"),
    path("", OrderList.as_view(), name="order_list")
]