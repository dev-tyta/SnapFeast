from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import UserEmbeddings

class UserTests(APITestCase):
    def setUp(self):
        # Create a user for testing logins and profile updates
        self.user = User.objects.create_user(username='testuser', password='testpassword123', email='test@example.com')

    def test_create_user(self):
        """
        Ensure we can create a new user and receive a success response.
        """
        url = reverse('signup')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'somepassword123',
            'password2': 'somepassword123',
            # Include other required fields
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_login_user(self):
        """
        Ensure we can log a user in and receive a token.
        """
        url = reverse('login')
        data = {
            'mail': 'test@example.com',
            'password': 'testpassword123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)

    def test_update_user_profile(self):
        """
        Ensure we can update the user profile.
        """
        self.client.login(mail='test@example.com', password='testpassword123')
        url = reverse('update-profile')
        data = {'username': 'updatedusername'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_facial_login(self):
        """
        Ensure facial login works with valid image data.
        """
        url = reverse('facial-login')
        # Assuming you have a way to simulate or mock the image data for tests
        data = {'image': 'base64_image_data_here'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('success' in response.data['status'])
