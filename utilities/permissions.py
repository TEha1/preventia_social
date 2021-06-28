from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission

User = get_user_model()


class IsActiveUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_active
