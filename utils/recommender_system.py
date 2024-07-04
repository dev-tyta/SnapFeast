import pandas as pd
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
import joblib
from django.core.cache import cache
from orders.models import MealOrder, Meal
from django.db.models import Prefetch
from django.db.models import Count
from django.utils import timezone
import os

class MealRecommender:
    def __init__(self):
        self.model_path = 'recommendation_model.joblib'
        self.last_train_path = 'last_train_time.txt'
        self.retrain_interval = timezone.timedelta(days=1)  # Retrain every 7 days
        self.algo = self.load_or_train_model()

    def fetch_data(self):
        orders = MealOrder.objects.all().values('user_id', 'meal_id', 'quantity')
        return pd.DataFrame(orders)

    def train_model(self):
        data = self.fetch_data()
        if data.empty:
            raise ValueError("No data available to train the model")
        
        reader = Reader(rating_scale=(1, 5))
        dataset = Dataset.load_from_df(data[['user_id', 'meal_id', 'quantity']], reader)
    
        trainset = dataset.build_full_trainset()
        algo = SVD()
        algo.fit(trainset)
        
        joblib.dump(algo, self.model_path)
        self._update_last_train_time()
        return algo

    def load_or_train_model(self):
        try:
            if self._should_retrain():
                return self.train_model()
            return joblib.load(self.model_path)
        except FileNotFoundError:
            return self.train_model()

    def _should_retrain(self):
        if not os.path.exists(self.last_train_path):
            return True
        with open(self.last_train_path, 'r') as f:
            last_train_time = timezone.datetime.fromisoformat(f.read().strip())
        return timezone.now() - last_train_time > self.retrain_interval

    def _update_last_train_time(self):
        with open(self.last_train_path, 'w') as f:
            f.write(timezone.now().isoformat())

    def get_recommendations(self, user):
        cache_key = f'user_recommendations_{user.id}'
        cached_recommendations = cache.get(cache_key)
        
        if self._should_retrain():
            self.algo = self.train_model()
            cache.clear()  # Clear all cached recommendations
            cached_recommendations = None

        if cached_recommendations:
            return cached_recommendations

        all_meals = Meal.objects.all()
        meal_ids = [meal.id for meal in all_meals]

        predictions = [self.algo.predict(str(user.id), str(meal_id)) for meal_id in meal_ids]
        sorted_predictions = sorted(predictions, key=lambda x: x.est, reverse=True)
        top_recommendations = Meal.objects.filter(pk__in=[int(pred.iid) for pred in sorted_predictions[:20]])
        top_recommendations = list(top_recommendations)

        top_recommendations = self.adjust_for_preferences(user, top_recommendations)

        cache.set(cache_key, top_recommendations, timeout=3600)  # Cache for 1 hour
        return top_recommendations

    def adjust_for_preferences(self, user, recommendations):
        preferences = user.preferences if hasattr(user, 'preferences') else {}
        preference_scores = {meal.id: 0 for meal in recommendations}

        for meal in recommendations:
            for key, weight in preferences.items():
                if key.lower() in meal.meal.lower():
                    preference_scores[meal.id] += weight

        sorted_recommendations = sorted(recommendations, key=lambda meal: preference_scores[meal.id], reverse=True)

        return sorted_recommendations[:3]  # Return top 3 after adjustment