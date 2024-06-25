from rest_framework import serializers

from .models import MealOrder


class MealOrderSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            "user_id",
            "food_type",
            "price",
            "date_created"
        )

        model = MealOrder