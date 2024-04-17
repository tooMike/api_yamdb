from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission
from rest_framework import permissions


User = get_user_model()


class AdminOnlyPermission(BasePermission):
    """Разрешаем доступ только админам и суперюзерам."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == 'admin' or request.user.is_superuser
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """Admin and Reading permissions."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and request.user.is_admin)
        )


class IsAdminModeratorAuthorReadOnly(permissions.BasePermission):
    """Permissions for Admin, Moderator, Author or Reader."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_admin
            or request.user.is_moderator
            or obj.author == request.user
        )
