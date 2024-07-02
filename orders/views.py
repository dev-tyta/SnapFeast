from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
import joblib
import numpy as np
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from .models import Meal, MealOrder
from .serializers import MealOrderSerializer, MealSerializer
from utils.recommender_system import MealRecommender


class CreateOrderView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MealOrderSerializer

    @extend_schema(
        description="Create a new meal order",
        responses={201: MealOrderSerializer},
        request=MealOrderSerializer,
        summary="Create a new meal order"
    )
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MealOrderSerializer

    @extend_schema(
        description="Retrieve, update, or delete a meal order",
        responses={
            200: MealOrderSerializer,
            404: {'description': 'Not found, no order with this ID exists for the user'},
            400: {'description': 'Bad request, invalid data'}
        },
        methods=['GET', 'PUT', 'DELETE'],
        summary="Manage a specific meal order"
    )
    def get_queryset(self):
        return MealOrder.objects.filter(user=self.request.user)


class OrderListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MealOrderSerializer

    @extend_schema(
        description="Retrieve a list of orders made by the logged-in user",
        responses={200: MealOrderSerializer(many=True)},
        summary="List user orders"
    )
    def get_queryset(self):
        return MealOrder.objects.filter(user=self.request.user)


class RecommendationView(APIView):
    permission_classes = [IsAuthenticated]
    recommender = MealRecommender()

    @extend_schema(
        description="Retrieve meal recommendations for the logged-in user based on their preferences and past orders.",
        responses={
            200: MealSerializer(many=True),
            404: {'description': 'No recommendations found'},
            500: {'description': 'Internal server error'}
        },
        summary="Get meal recommendations",
        tags=['Meal Recommendations']
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            recommendations = self.recommender.get_recommendations(user)
            if recommendations:
                serializer = MealSerializer(recommendations, many=True)
                return Response(serializer.data)
            else:
                return Response({"message": "No recommendations available"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
