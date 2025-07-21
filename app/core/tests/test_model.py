"""
Test for django models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models
from unittest.mock import patch


def create_user(*args, **kwargs):
    if not args and not kwargs:
        kwargs = {
            'email': 'test@example.com',
            'password': 'pass1234'
        }
    return get_user_model().objects.create_user(*args, **kwargs)


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a suer with an email is successful."""
        email = 'test@example.com'
        password = 'testpassword123'
        user = create_user(
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
            user = create_user(
                email=email,
                password="test@123"
            )
            self.assertEqual(user.email, normEmail)

    def test_create_user_empty_email_raises_value_error(self):
        """Check if empty emails raises value error"""
        test_func = create_user
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
        user = create_user(
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

    def test_create_tag(self):
        user = create_user()
        tag = models.Tag.objects.create(user=user, name='Tag1')
        self.assertEqual(str(tag), tag.name)

    def test_create_ingrediante(self):
        user = create_user()
        ingredient = models.Ingredients.objects.create(
            user=user,
            name='ing1',
        )

        self.assertEqual(str(ingredient), ingredient.name)

    @patch('core.models.uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'example.jpg')
        self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpg')
