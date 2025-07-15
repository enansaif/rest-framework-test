"""
Test for django models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a suer with an email is successful."""
        email = 'test@example.com'
        password = 'testpassword123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_create_user_with_email_normalized(self):
        """Check if the email addresses are normalzied"""
        test_emails = [
            ["test1@example.com", "test1@example.com"],
            ["TEST2@EXAMPLE.COM", "TEST2@example.com"]
        ]

        for email, normEmail in test_emails:
            user = get_user_model().objects.create_user(
                email=email,
                password="test@123"
            )
            self.assertEqual(user.email, normEmail)

    def test_create_user_empty_email_raises_value_error(self):
        """Check if empty emails raises value error"""
        test_func = get_user_model().objects.create_user
        self.assertRaises(ValueError, test_func, "", "pass@1234")

    def test_create_super_user(self):
        """Check if super user is created successfully"""
        user = get_user_model().objects.create_superuser(
            email="test@example.com",
            password="test123"
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_recipe_model_create(self):
        user = get_user_model().objects.create(
            email="test@1234",
            password='testpass1234',
            name='Test User',
        )
        price = 5.5
        recipe = models.Recipe.objects.create(
            user=user,
            title='title',
            description='description',
            price=price,
            link='a/b/c',
            time_minutes=5,
        )
        self.assertEqual(recipe.price, price)
