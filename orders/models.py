from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class Meal(models.Model):
    FOOD_TYPE_CHOICES = [
        ('AMALA', 'Amala'),
        ('PIZZA', 'Pizza'),
        ('BURGER', 'Burger')
    ]
    meal = models.CharField(
        max_length=50, 
        choices=FOOD_TYPE_CHOICES,
        null=True
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)],
        null=True
    )
    
    def __str__(self):
        return f"{self.meal} costs {self.price}"


class MealOrder(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        null=True,
        related_name='meal_orders'
    )

    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, null=True)

    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)],
        null=True
    )
    quantity = models.PositiveIntegerField(null=True)
    date_ordered = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.meal} ordered by {self.user.username} on {self.date_ordered.strftime('%Y-%m-%d')}"
