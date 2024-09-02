from django.contrib import admin
from .models import Meal, MealOrder, RecommendationModel

@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ['meal', 'price']

@admin.register(MealOrder)
class MealOrderAdmin(admin.ModelAdmin):
    list_display = ['meal', 'user', 'quantity', 'date_ordered']

@admin.register(RecommendationModel)
class RecommendationModelAdmin(admin.ModelAdmin):
    list_display = ['created_at']
