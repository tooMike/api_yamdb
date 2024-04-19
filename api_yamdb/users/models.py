from django.contrib.auth.models import AbstractUser
from django.db import models

from users.constants import (CONFIRMATION_CODE_MAX_LENGTH, ROLE_MAX_LENGTH,
                             USERNAME_MAX_LENGTH, Roles)
from users.validators import username_validator


class YamdbUser(AbstractUser):
    """Измененная модель юзера."""

    username = models.CharField(
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        validators=(username_validator,)
    )
    bio = models.TextField('Биография', blank=True)
    role = models.CharField(
        'Роль',
        max_length=ROLE_MAX_LENGTH,
        choices=Roles.choices,
        default=Roles.USER
    )
    email = models.EmailField('email address', unique=True)
    confirmation_code = models.CharField(
        max_length=CONFIRMATION_CODE_MAX_LENGTH
    )

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    @property
    def is_admin(self):
        """Возвращает True, если у пользователя права администратора."""
        return self.role == Roles.ADMIN or self.is_superuser or self.is_staff


    @property
    def is_moderator(self):
        """Возвращает True, если у пользователя права модератора."""
        return self.role == Roles.MODERATOR
