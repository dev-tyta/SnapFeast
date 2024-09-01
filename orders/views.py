from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from .models import Meal, MealOrder
from .serializers import MealOrderSerializer, MealSerializer
from utils.recommender_system import MealRecommender
from django.db.models import Prefetch
from rest_framework.authentication import TokenAuthentication

class CreateOrderView(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = MealOrderSerializer

    @extend_schema(
        description="Create a new meal order",
        responses={
            201: MealOrderSerializer,
            400: {"description": "Bad request, invalid data"}
        },
        request=MealOrderSerializer,
        summary="Create a new meal order"
    )
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = MealOrderSerializer

    @extend_schema(
        description="Retrieve, update, or delete a meal order",
        responses={
            200: MealOrderSerializer,
            404: {'description': 'Not found, no order with this ID exists for the user'},
            400: {'description': 'Bad request, invalid data'}
        },
        methods=['GET', 'PUT', 'PATCH', 'DELETE'],
        summary="Manage a specific meal order"
    )
    def get_object(self):
        queryset = MealOrder.objects.filter(user=self.request.user)
        obj = get_object_or_404(queryset, pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderListView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = MealOrderSerializer

    @extend_schema(
        description="Retrieve a list of orders made by the logged-in user",
        responses={200: MealOrderSerializer(many=True)},
        summary="List user orders"
    )
    def get_queryset(self):
        return MealOrder.objects.filter(user=self.request.user).select_related('meal')


class RecommendationView(APIView):
    authentication_classes = [TokenAuthentication]
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
                return Response({"message": "No recommendations available"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)