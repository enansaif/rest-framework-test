from django.urls import reverse
from rest_framework.test import APIClient
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
USER_TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**kwargs):
    return get_user_model().objects.create_user(**kwargs)


class PublicAPITest(TestCase):
    """Testing the apis that doesn't require login"""
    def setUp(self):
        self.client = APIClient()

    def test_check_user_login_success(self):
        payload = {
            'email': "test@example.com",
            'password': "test1234",
            'name': 'Test User',
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        """Test error returned if user with email exists"""
        payload = {
            'email': "test@example.com",
            'password': "test1234",
            'name': 'Test User',
        }

        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_password_too_short(self):
        """Test if user password too short"""
        payload = {
            'email': "test@example.com",
            'password': "pw",
            'name': 'Test User',
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        user_info = {
            'email': 'test@example.com',
            'password': 'test1234',
            'name': 'Test User',
        }
        create_user(**user_info)

        payload = {
            'email': user_info['email'],
            'password': user_info['password'],
        }
        res = self.client.post(USER_TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_create_token_wrong_password(self):
        user_info = {
            'email': 'test@example.com',
            'password': 'test1234',
            'name': 'Test User',
        }
        create_user(**user_info)

        payload = {
            'email': user_info['email'],
            'password': 'badpass',
        }
        res = self.client.post(USER_TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_create_token_blank_password(self):
        user_info = {
            'email': 'test@example.com',
            'password': 'test1234',
            'name': 'Test User',
        }
        create_user(**user_info)

        payload = {
            'email': user_info['email'],
            'password': '',
        }
        res = self.client.post(USER_TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_retriever_user_unauthorized(self):
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAPITest(TestCase):
    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test User',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_me_not_allowed(self):
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        payload = {
            'name': 'New Name',
            'password': 'newpass123',
        }
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
