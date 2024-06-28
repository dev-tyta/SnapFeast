from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import MealOrder
from .serializers import MealOrderSerializer

# Views for handling orders
class CreateOrderView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MealOrderSerializer

    def perform_create(self, serializer):
        # Associating the order with the currently logged-in user
        serializer.save(user=self.request.user)

class OrderListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MealOrderSerializer

    def get_queryset(self):
        # Ensuring users can only see their own orders
        return MealOrder.objects.filter(user=self.request.user)

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MealOrderSerializer

    def get_queryset(self):
        # Ensuring users can only access their own orders
        return MealOrder.objects.filter(user=self.request.user)
