from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
import joblib
import numpy as np
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Meal, MealOrder
from .serializers import MealOrderSerializer, MealSerializer
from utils.recommender_system import MealRecommender


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
 

class RecommendationView(APIView):
    permission_classes = [IsAuthenticated]
    recommender = MealRecommender()

    def get(self, request, *args, **kwargs):
        user = request.user
        recommendations = self.recommender.get_recommendations(user)
        serializer = MealSerializer(recommendations, many=True)
        return Response(serializer.data)
