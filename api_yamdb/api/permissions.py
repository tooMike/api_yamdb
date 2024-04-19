from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework.permissions import BasePermission


User = get_user_model()


class IsSuperUserOrIsAdmin(BasePermission):
    """Разрешаем доступ только админам и суперюзерам."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


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
