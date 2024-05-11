from django.test import SimpleTestCase

# Create your tests here.

class SimpleTests(SimpleTestCase):
    def test_welcome_page_status_code(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_login_page_status_code(self):
        response = self.client.get("/login/")
        self.assertEqual(response.status_code, 200)