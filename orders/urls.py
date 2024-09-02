from django.urls import path
from .views import OrderListView, OrderDetailView, CreateOrderView, RecommendationView
from .views import MealCreateView, MealDetailView, MealListView

app_name = 'orders'  # Useful for namespacing and reversing URLs

urlpatterns = [
    path("", CreateOrderView.as_view(), name="create"),  # POST here creates a new order
    path("<int:pk>/", OrderDetailView.as_view(), name="detail"),  # GET, PUT, DELETE on individual order
    path("list/", OrderListView.as_view(), name="list"),  # GET list of all orders for the user
    path('meals/', MealCreateView.as_view(), name='meal-create'),
    path('meals/<int:pk>/', MealDetailView.as_view(), name='meal-detail'),
    path('meals/list/', MealListView.as_view(), name='meal-list'),
    path("recommendations/", RecommendationView.as_view(), name="recommendations"),  # GET recommended meals
]