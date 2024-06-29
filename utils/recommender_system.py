import pandas as pd
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
import joblib
from orders.models import MealOrder, Meal


class MealRecommender:
# Fetch data from your database
    def fetch_data(self):
        orders = MealOrder.objects.all().values('user_id', 'meal_id', 'quantity')
        return pd.DataFrame(orders)

    def train_model(self):
        data = self.fetch_data()
        reader = Reader(rating_scale=(1, 5))
        dataset = Dataset.load_from_df(data[['user_id', 'meal_id', 'quantity']], reader)
    
        trainset, testset = train_test_split(dataset, test_size=0.1)
        self.algo = SVD()
        self.algo.fit(trainset)


    def get_recommendations(self, user):
        all_meals = Meal.objects.all()
        meal_ids = [meal.id for meal in all_meals]

        predictions = [self.algo.predict(user.id, meal_id) for meal_id in meal_ids]
        sorted_predictions = sorted(predictions, key=lambda x: x.est, reverse=True)
        top_recommendations = [Meal.objects.get(pk=pred.iid) for pred in sorted_predictions[:10]]

        # Adjust recommendations based on user preferences
        top_recommendations = self.adjust_for_preferences(user, top_recommendations)

        return top_recommendations

    def adjust_for_preferences(self, user, recommendations):
        preferences = user.preferences or {}
        preference_scores = {meal.id: 0 for meal in recommendations}

        for meal in recommendations:
            for key, weight in preferences.items():
                if key.lower() in meal.description.lower() or key.lower() in meal.category.lower():
                    preference_scores[meal.id] += weight

        # Sort recommendations based on preference scores
        sorted_recommendations = sorted(recommendations, key=lambda meal: preference_scores[meal.id], reverse=True)

        return sorted_recommendations
