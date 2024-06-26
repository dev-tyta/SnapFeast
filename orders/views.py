from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import MealOrder
from .serializers import MealOrderSerializer


# Create your views here.
class CreateOrderView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = MealOrder.objects.all()
    serializer_class = MealOrderSerializer

    def perform_create(self, serializer):
        serializer.save(user_id = self.request.user)


class OrderList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = MealOrder.objects.all()
    serializer_class = MealOrderSerializer

    def get_queryset(self):
        return self.queryset.filter(user_id=self.request.user)


class OrderDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = MealOrder.objects.all()
    serializer_class = MealOrderSerializer
