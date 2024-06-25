from django.urls import path

from .views import OrderList, OrderDetail


urlpatterns = [
    path("<int:pk>/", OrderDetail.as_view(), name="order_details"),
    path("", OrderList.as_view(), name="order_list")
]