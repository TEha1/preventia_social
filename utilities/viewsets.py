from django.contrib.auth import get_user_model
from django.db.models import Q
from django_filters import BooleanFilter
from django_filters.rest_framework import FilterSet
from drf_yasg import openapi
from posts.models import Like, Post
from users.models import FriendShip

User = get_user_model()


class UserFilterClass(FilterSet):
    friends = BooleanFilter(method='filter_friends')

    class Meta:
        model = User
        fields = []

    def filter_friends(self, queryset, name, value):
        if value:
            friend_ships = FriendShip.objects.filter(
                Q(sender_id=self.request.user.id) |
                Q(receiver_id=self.request.user.id)
            )
            queryset = queryset.filter(
                Q(pk__in=friend_ships.values('sender_id')) |
                Q(pk__in=friend_ships.values('receiver_id'))
            )
        return queryset


class PostFilterClass(FilterSet):
    is_liked = BooleanFilter(method='filter_is_liked')

    class Meta:
        model = Post
        fields = [
            'user',
            'is_draft',
        ]

    def filter_is_liked(self, queryset, name, value):
        if value:
            queryset = queryset.filter(
                pk__in=Like.objects.filter(user=self.request.user).values_list('post_id', flat=True)
            )
        return queryset


user_field_expand = [
    openapi.Parameter('friends', in_=openapi.IN_QUERY,
                      description="Filter the returned users list with the authentication user friends.",
                      type=openapi.TYPE_BOOLEAN),
    openapi.Parameter('ordering', in_=openapi.IN_QUERY, enum=['created_at', '-created_at', 'username', '-username', ],
                      description="Ordering the returned users list.",
                      type=openapi.TYPE_STRING),
    openapi.Parameter('page_size', in_=openapi.IN_QUERY, required=True, default=20,
                      description="Number of results to return per page.",
                      type=openapi.TYPE_INTEGER),
]

post_field_expand = [
    openapi.Parameter('is_liked', in_=openapi.IN_QUERY,
                      description="Filter the returned posts list with the authentication user likes.",
                      type=openapi.TYPE_BOOLEAN),
    openapi.Parameter('ordering', in_=openapi.IN_QUERY, enum=['created_at', '-created_at', 'text', '-text', ],
                      description="Ordering the returned posts list.",
                      type=openapi.TYPE_STRING),
    openapi.Parameter('page_size', in_=openapi.IN_QUERY, required=True, default=20,
                      description="Number of results to return per page.",
                      type=openapi.TYPE_INTEGER),
]

friendship_field_expand = [
    openapi.Parameter('status', in_=openapi.IN_QUERY, enum=["waiting", "accepted"],
                      description="Filter the returned friendships list with the status value.",
                      type=openapi.TYPE_STRING),
    openapi.Parameter('ordering', in_=openapi.IN_QUERY, enum=['created_at', '-created_at', ],
                      description="Ordering the returned friendships list.",
                      type=openapi.TYPE_STRING),
    openapi.Parameter('page_size', in_=openapi.IN_QUERY, required=True, default=20,
                      description="Number of results to return per page.",
                      type=openapi.TYPE_INTEGER),
]

comment_field_expand = [
    openapi.Parameter('ordering', in_=openapi.IN_QUERY, enum=['created_at', '-created_at', 'text', '-text', ],
                      description="Ordering the returned posts list.",
                      type=openapi.TYPE_STRING),
    openapi.Parameter('page_size', in_=openapi.IN_QUERY, required=True, default=20,
                      description="Number of results to return per page.",
                      type=openapi.TYPE_INTEGER),
]

attachment_field_expand = [
    openapi.Parameter('page_size', in_=openapi.IN_QUERY, required=True, default=20,
                      description="Number of results to return per page.",
                      type=openapi.TYPE_INTEGER),
]
