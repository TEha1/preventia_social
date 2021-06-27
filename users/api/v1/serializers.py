from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm
from django.utils.translation import gettext_lazy as _
from django_restql.mixins import DynamicFieldsMixin
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueTogetherValidator

from users.models import FriendShip

User = get_user_model()


class UserSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    new_password1 = serializers.CharField(max_length=128, write_only=True)
    new_password2 = serializers.CharField(max_length=128, write_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'personal_image',
            'role',
            'new_password1',
            'new_password2',
        ]

    def validate(self, attrs):
        password = attrs.get('new_password1', None)
        if password is None:
            return attrs

        set_password_form = SetPasswordForm(
            user=self, data=attrs
        )
        if not set_password_form.is_valid():
            raise serializers.ValidationError(set_password_form.errors)
        return attrs

    def create(self, validated_data):
        try:
            validated_data.pop('new_password1')
            new_password2 = validated_data.pop('new_password2')
            user = super(UserSerializer, self).create(validated_data)
        except Exception as e:
            raise serializers.ValidationError({"error": [e]})
        user.set_password(new_password2)
        user.save()
        return user

    def update(self, instance, validated_data):
        validated_data.pop('new_password1', None)
        validated_data.pop('new_password2', None)

        return super(UserSerializer, self).update(instance, validated_data)


class UserDetailsSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'personal_image',
            'role',
        ]

    def to_representation(self, user):
        data = super(UserDetailsSerializer, self).to_representation(user)
        data['role'] = {
            'key': user.role,
            'value': user.get_role_display()
        }
        return data


class UserLoginDataSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'token',
            'id',
            'username',
            'email',
            'role',
        ]

    def get_token(self, user):
        token, created = Token.objects.get_or_create(user=user)
        return token.key


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class FriendShipSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = FriendShip
        fields = [
            'id',
            'sender',
            'receiver',
            'status',
        ]
        validators = [
            UniqueTogetherValidator(
                queryset=FriendShip.objects.all(),
                fields=['sender', 'receiver'],
                message=_("You already sent a friendship request.")
            )
        ]

    def to_representation(self, friend_ship):
        data = super(FriendShipSerializer, self).to_representation(friend_ship)
        data['sender'] = UserDetailsSerializer(
            friend_ship.sender,
            context=self.context
        ).data
        data['receiver'] = UserDetailsSerializer(
            friend_ship.receiver,
            context=self.context
        ).data
        return data
