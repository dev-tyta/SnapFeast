from rest_framework import generics

from .models import MealOrder
from .serializers import MealOrderSerializer


# Create your views here.
class OrderList(generics.ListCreateAPIView):
    queryset = MealOrder.objects.all()
    serializer_class = MealOrderSerializer


class OrderDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = MealOrder.objects.all()
    serializer_class = MealOrderSerializer

