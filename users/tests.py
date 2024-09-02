from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import UserEmbeddings
from unittest.mock import patch
import base64

class UserTests(APITestCase):

    def setUp(self):
        # Create a user for testing logins and profile updates
        self.user = User.objects.create_user(username='newuser@example.com', password='testpassword123', email='test@example.com')
        self.client.login(username='newuser@example.com', password='testpassword123')

    def test_create_user(self):
        """
        Ensure we can create a new user and receive a success response.
        """
        url = reverse('signup')  # Make sure this matches the actual URL name in your Django URLs
        data = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'age': 25,
            'preferences': ['Some preferences'],
            'password1': 'somepassword123',
            'password2': 'somepassword123',
            # Include other required fields like 'first_name', 'last_name', etc., if necessary
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_user(self):
        """
        Ensure we can log a user in and receive a token.
        """
        url = reverse('login')  # Make sure this matches the actual URL name in your Django URLs
        data = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)

    def test_update_user_profile(self):
        """
        Ensure we can update the user profile.
        """
        url = reverse('update-profile')  # Make sure this matches the actual URL name in your Django URLs
        data = {'email': 'updatenewuser@example.com'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'updatedusername')

    @patch('path.to.FacialProcessing.extract_embeddings')
    @patch('path.to.FacialProcessing.face_extract')
    def test_facial_login(self, mock_face_extract, mock_extract_embeddings):
        """
        Ensure facial login works with valid image data.
        """
        # Prepare mock data
        mock_face_extract.return_value = 'mock_face_data'
        mock_extract_embeddings.return_value = [0.1, 0.2, 0.3, 0.4]

        # Create a UserEmbeddings entry for the test user
        UserEmbeddings.objects.create(user=self.user, embeddings=[0.1, 0.2, 0.3, 0.4])

        url = reverse('facial-login')  # Make sure this matches the actual URL name in your Django URLs
        image_data = base64.b64encode(b'test image data').decode('utf-8')  # Simulate a base64 image string
        data = {'image': image_data}
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('Success' in response.data['status'])

