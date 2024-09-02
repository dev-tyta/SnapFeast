import pandas as pd
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
from django.core.cache import cache
from orders.models import MealOrder, Meal
from django.utils import timezone
from orders.models import RecommendationModel
import random
import pickle
from orders.models import RecommendationModel

class MealRecommender:
    def __init__(self):
        self.retrain_interval = timezone.timedelta(days=1)  # Retrain every day
        self.algo = self.load_or_train_model()

    def fetch_data(self):
        orders = MealOrder.objects.all().values('user_id', 'meal_id', 'quantity')
        return pd.DataFrame(list(orders))

    def train_model(self):
        data = self.fetch_data()
        if data.empty:
            self.algo = None
            return None
        
        reader = Reader(rating_scale=(1, 5))
        dataset = Dataset.load_from_df(data[['user_id', 'meal_id', 'quantity']], reader)
    
        trainset = dataset.build_full_trainset()
        algo = SVD()
        algo.fit(trainset)
        
        # Serialize the trained model and save it in the database
        model_binary = pickle.dumps(algo)
        model_record = RecommendationModel(model=model_binary, created_at=timezone.now())
        model_record.save()

        return algo

    def load_or_train_model(self):
        latest_model = RecommendationModel.objects.order_by('-created_at')

        if latest_model and timezone.now() - latest_model.created_at <= self.retrain_interval:
            return pickle.loads(latest_model.model)
        else:
            return self.train_model()

    def _should_retrain(self):
        latest_model = RecommendationModel.objects.order_by('-created_at').first()
        if not latest_model:
            return True
        return timezone.now() - latest_model.created_at > self.retrain_interval

    def get_recommendations(self, user):
        cache_key = f'user_recommendations_{user.id}'
        cached_recommendations = cache.get(cache_key)
        
        if self._should_retrain():
            self.algo = self.train_model()
            cache.clear()  # Clear all cached recommendations
            cached_recommendations = None

        if cached_recommendations:
            return cached_recommendations

        if self.algo is None:
            return self.get_random_recommendations()

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

    def get_random_recommendations(self):
        all_meals = list(Meal.objects.all())
        return random.sample(all_meals, min(3, len(all_meals)))
