from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import MealOrder, Meal
from decimal import Decimal
from users.serializers import UserProfileSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'user_id')


class MealSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        min_value=Decimal('0.01'),  # Ensure price is greater than zero
        error_messages={
            "min_value": "Price must be greater than zero."
        }
    )

    class Meta:
        model = Meal
        fields = '__all__'


class MealOrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    price = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        min_value=Decimal('0.01')
    )
    quantity = serializers.IntegerField(
        min_value=1,  # Quantity must be greater than zero
        error_messages={
            "min_value": "Quantity must be greater than zero."
        }
    )

    class Meta:
        model = MealOrder
        fields = ('user', 'meal', "quantity", 'price', 'date_ordered')
        read_only_fields = ('date_ordered',)  # Making date_ordered read-only

    def validate_price(self, value):
        """
        Check that the price is not negative.
        """
        if value < 0:
            raise serializers.ValidationError("Price must be a positive number.")
        return value


class RecommendationSerializer(serializers.Serializer):
    meal_id = serializers.IntegerField()
    name = serializers.CharField(max_length=255)
    description = serializers.CharField()
    price = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2,
        min_value=Decimal('0.01')
    )
    score = serializers.FloatField()

    class Meta:
        fields = ('meal_id', 'name', 'description', 'price', 'score')
