from django.test import TestCase
from django.contrib.auth import get_user_model

from .models import MealOrder


# Create your tests here.
class OrderTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username = "testuser",
            email = "test@email.com",
            password = "secret",
        )

        cls.orders = MealOrder.objects.create(
            user_id = cls.user,
            food_type = "Amala",
            price = 20000,
        )

    def test_order_model(self):
        self.assertEqual(self.orders.user_id.username, "testuser")
        self.assertEqual(self.orders.food_type, "Amala")
        self.assertEqual(self.orders.price, 20000)
        self.assertEqual(str(self.orders), "Amala")
        