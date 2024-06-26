import pandas as pd
from src.orders.models import MealOrder

def create_user_item_matrix():
    orders = MealOrder.objects.all().values("user_id", "food_type", "date_ordered")
    df = pd.DataFrame(orders)
    user_item_matrix = df.pivot_table(index="user_id", columns="food_type", values="date_ordered", aggfunc="count", fill_value=0)\

    return user_item_matrix
