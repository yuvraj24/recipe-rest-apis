from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**param):
    return get_user_model().objects.create_user(**param)


class PublicUserApiTest(TestCase):
    # Test the users api (public)

    def setUp(self) -> None:
        self.client = APIClient()

    def test_create_valid_user_success(self):
        # Test creating valid payload is successful
        payload = {
            'email': 'yuvraj@gmail.com',
            'password': 'test123',
            'name': 'Yuvraj Pandey'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        # Test creating a user that already exists fails
        payload = {'email': 'yuvraj@gmail.com', 'password': 'test@123',
                   'name': 'Yuvraj Pandey'}
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        # Test that password must be more than 5 characters
        payload = {'email': 'yuvraj@gmail.com', 'password': 'test',
                   'name': 'Yuvraj Pandey'}
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def create_token_for_user(self):
        # Test that a token is created for the user
        payload = {
            'email': 'yuvraj@gmail.com',
            'password': 'test123',
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        # Test that token is not created if invalid credentials are given
        create_user(email='yuvraj@gmail.com', password='test123')
        payload = {
            'email': 'yuvraj@gmail.com',
            'password': 'wrong',
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        # Test that token is not created if user dosen't exists
        payload = {
            'email': 'yuvraj@gmail.com',
            'password': 'test123',
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        # Test that email & password are required
        payload = {
            'email': 'yuvraj@gmail.com',
            'password': '',
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
