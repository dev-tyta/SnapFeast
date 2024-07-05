from django.db import models
from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator


class Meal(models.Model):
    FOOD_TYPE_CHOICES = [
        ('Amala with Goat Meat', 'Amala with Goat Meat'),
        ('Jollof and Fried Rice with Chicken', 'Jollof and Fried Rice with Chicken'),
        ('Porridge with Vegetable', 'Porridge with Vegetable'),
        ('Pounded Yam with Egusi Soup','Pounded Yam with Egusi Soup'),
        ('White Rice, Beans and Fried Stew','White Rice, Beans and Fried Stew'),
        ('Yam and Fried Eggs','Yam and Fried Eggs'),
        ('Spaghetti Bolognese with Sauce', 'Spaghetti Bolognese with Sauce'),
        ('Chicken and Chips', 'Chicken and Chips'),
        ('Fruit Salad', 'Fruit Salad'),

    ]
    meal = models.CharField(
        max_length=500, 
        choices=FOOD_TYPE_CHOICES,
        null=True
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        min_value=Decimal('0.01'),
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
