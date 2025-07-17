from django.test import TestCase
from rest_framework.test import APIClient
from core.models import Ingredients
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse('recipe:ingredients-list')


def detail_url(ingredient_id):
    return reverse('recipe:ingredients-detail', args=[ingredient_id])


def create_user(*args, **kwargs):
    if not args and not kwargs:
        kwargs = {
            'email': 'user@example.com',
            'password': 'testpass123'
        }
    return get_user_model().objects.create_user(*args, **kwargs)


class PublicApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    def test_list_all_ingredient(self):
        Ingredients.objects.create(user=self.user, name='kale')
        Ingredients.objects.create(user=self.user, name='corn')
        res = self.client.get(INGREDIENT_URL)
        ingredients = Ingredients.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_list_ingredient_authorized_only(self):
        ingredient = Ingredients.objects.create(user=self.user, name='kale')
        user = create_user(email='test@example.com', password='test1234')
        Ingredients.objects.create(user=user, name='pepper')
        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)

    def test_update_ingredient(self):
        ingredient = Ingredients.objects.create(
            user=self.user, name='cilantro'
        )

        payload = {
            'name': 'onion'
        }
        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])
