from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import UserProfile, UserEmbeddings
from django.core.files.uploadedfile import SimpleUploadedFile

class UserTests(APITestCase):
    def setUp(self):
        self.user = UserProfile.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123',
            first_name='Test',
            last_name='User',
            age=30
        )
        self.image = SimpleUploadedFile("face.jpg", b"file_content", content_type="image/jpeg")

    def test_user_signup(self):
        url = reverse('user_signup')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'somepassword123',
            'first_name': 'New',
            'last_name': 'User',
            'age': 25,
            'preferences': 'Vegetarian',
            'image': self.image
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_email_login(self):
        url = reverse('email_login')
        data = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_face_login(self):
        # First, update the user's face data
        update_url = reverse('update_face')
        self.client.force_authenticate(user=self.user)
        update_response = self.client.post(update_url, {'image': self.image}, format='multipart')
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)

        # Now try face login
        url = reverse('face_login')
        login_response = self.client.post(url, {'image': self.image}, format='multipart')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', login_response.data)
        self.assertIn('refresh', login_response.data)

    def test_update_user_profile(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('update_profile')
        data = {'username': 'updatedusername', 'age': 31}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'updatedusername')
        self.assertEqual(self.user.age, 31)

    def test_invalid_login(self):
        url = reverse('email_login')
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)