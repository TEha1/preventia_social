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


class PostTest(CustomAPITestCase):
    def setUp(self) -> None:
        self.token = self.frequent_objects.create_user()
        self.valid_payload = {
            "text": "post content post content post content post content post content post content post content "
                    "post content post content post content post content post content post content post content "
                    "post content post content post content post content post content post content post content ",
            "is_draft": False
        }
        self.invalid_payload = {
            "is_draft": 20
        }

    def test_valid_post(self):
        self.client.credentials(HTTP_AUTHORIZATION=f' Token {self.token}')
        response = self.client.post(
            path=reverse('posts:posts-list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        id = response.json()['id']

        # Like Dislike Post
        self.client.credentials(HTTP_AUTHORIZATION=f' Token {self.token}')
        response = self.client.post(
            path=reverse('posts:posts-like_dislike', kwargs={'pk': id}),
            data=json.dumps({}),
            content_type='application/json'
        )
        print(response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_post(self):
        self.client.credentials(HTTP_AUTHORIZATION=f' Token {self.token}')
        response = self.client.post(
            path=reverse('posts:posts-list'),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CommentTest(CustomAPITestCase):
    def setUp(self) -> None:
        self.token = self.frequent_objects.create_user()
        self.client.credentials(HTTP_AUTHORIZATION=f' Token {self.token}')
        response = self.client.post(
            path=reverse('posts:posts-list'),
            data=json.dumps({
                "text": "post content post content post content post content post content post content post content "
                        "post content post content post content post content post content post content post content "
                        "post content post content post content post content post content post content post content ",
                "is_draft": False
            }),
            content_type='application/json'
        )
        post_id = response.json()['id']
        self.valid_comment_payload = {
            "post": f'{post_id}',
            'text': "good post",
        }
        self.invalid_comment_payload = {
            "post": -1,
            'text': True
        }

    def test_valid_comment(self):
        response = self.client.post(
            path=reverse('posts:comments-list'),
            data=json.dumps(self.valid_comment_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invalid_comment(self):
        response = self.client.post(
            path=reverse('posts:comments-list'),
            data=json.dumps(self.invalid_comment_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

