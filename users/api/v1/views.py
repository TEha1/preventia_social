from django.contrib.auth import get_user_model, authenticate
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from users.models import FriendShip
from utilities.exceptions import Http400
from utilities.viewsets import UserFilterClass, user_field_expand, friendship_field_expand
from users.api.v1.serializers import (
    UserDetailsSerializer, UserSerializer, UserLoginDataSerializer, LoginSerializer,
    FriendShipSerializer
)

User = get_user_model()


@method_decorator(name='list', decorator=swagger_auto_schema(manual_parameters=user_field_expand))
class UserResource(ModelViewSet):
    authentication_classes = []
    permission_classes = []
    queryset = User.objects.filter(is_superuser=False, is_staff=False, is_active=True).order_by('-created_at')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        'friends',
    ]
    filter_class = UserFilterClass
    search_fields = [
        'username',
        'email',
    ]
    ordering_fields = [
        'created_at',
        'username',
    ]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve', ]:
            return UserDetailsSerializer
        return UserSerializer

    def perform_create(self, serializer):
        return serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = UserLoginDataSerializer(user, many=False, context={'request': request}).data
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class LoginAPIView(GenericAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = authenticate(request=request, username=data['username'], password=data['password'])
        if user:
            return Response({
                'data': UserLoginDataSerializer(user, context={'request': request}).data
            }, status=status.HTTP_200_OK)

        raise AuthenticationFailed()


@method_decorator(name='list', decorator=swagger_auto_schema(manual_parameters=friendship_field_expand))
class FriendShipResource(ModelViewSet):
    serializer_class = FriendShipSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = [
        'status',
    ]
    ordering_fields = [
        'created_at',
    ]

    def get_queryset(self):
        return FriendShip.objects.filter(receiver_id=self.request.user.id).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        request.POST._mutable = True
        request.data.update({
            'sender': str(self.request.user.id)
        })
        request.POST._mutable = False
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(methods=['post', ], detail=True, url_path='accept-friendship', url_name='accept_friendship', )
    def accept_friendship(self, request, pk):
        friendship = self.get_object()
        if friendship.status == FriendShip.WAITING:
            friendship.accept()
            return Response(
                {"details": _("friendship request has been accepted"), },
                status=status.HTTP_200_OK
            )
        raise Http400(_("not available"))

    @action(methods=['post', ], detail=True, url_path='reject-friendship', url_name='reject_friendship', )
    def reject_friendship(self, request, pk):
        friendship = self.get_object()
        if friendship.status in [FriendShip.WAITING, FriendShip.ACCEPTED]:
            friendship.delete()
            return Response(
                {"details": _("friendship request has been rejected"), }, status=status.HTTP_200_OK,
            )
        raise Http400(_("not available"))
