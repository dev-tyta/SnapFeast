from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import MealOrder

class OrderTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@email.com",
            password="secret",
        )

        cls.order = MealOrder.objects.create(
            user=cls.user,
            food_type="Amala",
            price=200.00,  # Assuming a realistic price
        )

    def test_order_attributes(self):
        """Test attributes of the order model."""
        order = self.order
        self.assertEqual(order.user.username, "testuser")
        self.assertEqual(order.food_type, "Amala")
        self.assertEqual(order.price, 200.00)
        self.assertIn("Amala", str(order))  # Adjusted based on the new __str__ method
        self.assertIn("testuser", str(order))  # Check if username is part of the string representation
