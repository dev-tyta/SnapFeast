from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import MealOrder, Meal
from decimal import Decimal

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')

class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = '__all__'


class MealOrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    price = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        min_value=Decimal('0.01')  # Ensure min_value is a Decimal instance
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
