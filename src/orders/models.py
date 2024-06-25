from django.db import models
from django.conf import settings


# Create your models here.
class MealOrder(models.Model):
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    food_type = models.CharField(max_length=10, choices=[('CHOICE1', 'Amala'), ('CHOICE2', 'Choice 2'), ('CHOICE3', 'Choice 3')])
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date_ordered = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return self.food_type
