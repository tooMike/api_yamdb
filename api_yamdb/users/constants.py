"""Константы."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class Roles(models.TextChoices):
    """Возможные роли пользователей."""

    USER = "user", _("User")
    MODERATOR = "moderator", _("Moderator")
    ADMIN = "admin", _("Admin")


# Количество символов кода подтверждения
CONFIRMATION_CODE_LENGTH = 6

USERNAME_MAX_LENGTH = 150

ROLE_MAX_LENGTH = 50

CONFIRMATION_CODE_MAX_LENGTH = 50
