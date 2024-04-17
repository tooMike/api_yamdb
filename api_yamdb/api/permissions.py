from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission


User = get_user_model()


class AdminOnlyPermission(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.role == 'admin' or request.user.is_superuser)
