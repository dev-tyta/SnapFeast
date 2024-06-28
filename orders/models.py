from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class MealOrder(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='meal_orders'
    )
    FOOD_TYPE_CHOICES = [
        ('AMALA', 'Amala'),
        ('PIZZA', 'Pizza'),
        ('BURGER', 'Burger')
    ]
    food_type = models.CharField(
        max_length=50, 
        choices=FOOD_TYPE_CHOICES
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)]
    )
    date_ordered = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.food_type} ordered by {self.user.username} on {self.date_ordered.strftime('%Y-%m-%d')}"

