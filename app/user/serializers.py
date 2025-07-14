"""
Serializers for the user api views.
"""
from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}


    def create(self, kwargs):
        """
        Override the default create function so that it uses our
        create_user rather than saving whatever values we have
        passed through the serializer e.g. plaintext password.
        """
        return get_user_model().objects.create_user(**kwargs)