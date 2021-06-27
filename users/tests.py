import json
from django.urls import reverse
from django.utils.crypto import get_random_string
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from users.api.v1.serializers import UserSerializer


class FrequentlyUsedObjects:
    def create_user(self):
        num = get_random_string(length=4)
        serializer = UserSerializer(data={
            "username": f"user_{num}",
            "email": f"user_{num}@example.com",
            "new_password1": "Dx123123",
            "new_password2": "Dx123123",
        })
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Token.objects.create(user=user)


class CustomAPITestCase(APITestCase):
    frequent_class = FrequentlyUsedObjects

    def _pre_setup(self):
        super(CustomAPITestCase, self)._pre_setup()
        self.frequent_objects = self.frequent_class()


class UserTest(CustomAPITestCase):

    def setUp(self) -> None:
        self.valid_user_payload = {
            "username": "user_01",
            "email": "user_01@example.com",
            "new_password1": "Dx123123",
            "new_password2": "Dx123123",
        }
        self.invalid_user_payload = {
            "username": "user_01",
            "email": "user_01",
            "new_password1": "123",
            "new_password2": "123",
        }
        self.valid_login_payload = {
            "username": "user_01",
            "password": "Dx123123",
        }
        self.invalid_login_payload = {
            "username": "user_01",
            "password": "Dx1231@@",
        }

    def test_valid_create_user(self):
        """
        Ensure we can create a new doctor object.
        """
        response = self.client.post(
            path=reverse('users:users-list'),
            data=json.dumps(self.valid_user_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invalid_create_doctor(self):
        """
        Ensure we can not create a new doctor object with invalid data.
        """
        response = self.client.post(
            path=reverse('users:users-list'),
            data=json.dumps(self.invalid_user_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_valid_login(self):
        serializer = UserSerializer(data=self.valid_user_payload)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = self.client.post(
            path=reverse('users:login'),
            data=json.dumps(self.valid_login_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_login(self):
        serializer = UserSerializer(data=self.valid_user_payload)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = self.client.post(
            path=reverse('users:login'),
            data=json.dumps(self.invalid_login_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_inactive_login(self):
        serializer = UserSerializer(data=self.valid_user_payload)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.is_active = False
        user.save()
        response = self.client.post(
            path=reverse('users:login'),
            data=json.dumps(self.valid_login_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class FriendShipTest(CustomAPITestCase):
    def setUp(self) -> None:
        self.token1 = self.frequent_objects.create_user()
        self.token2 = self.frequent_objects.create_user()
        self.valid_payload = {
            "receiver": f"{self.token2.user_id}",
        }
        self.invalid_payload = {
            "receiver": "-1",
        }

    def test_valid_send_friendship_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=f' Token {self.token1}')
        response = self.client.post(
            path=reverse('users:friendships-list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        id = response.json()['id']
        self.client.credentials(HTTP_AUTHORIZATION=f' Token {self.token2}')

        # Accept Request
        response = self.client.post(
            path=reverse('users:friendships-accept_friendship', kwargs={'pk': id}),
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # reject Request
        response = self.client.post(
            path=reverse('users:friendships-reject_friendship', kwargs={'pk': id}),
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_friendship_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=f' Token {self.token1}')
        response = self.client.post(
            path=reverse('users:friendships-list'),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
