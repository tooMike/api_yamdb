from django.contrib.auth.models import AbstractUser
from django.db import models

from users.constants import CHOICES
from users.validators import username_validator


class MyUser(AbstractUser):
    """Измененная модель юзера."""

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[username_validator]
    )
    bio = models.TextField('Биография', blank=True)
    role = models.CharField(
        'Роль', max_length=50, choices=CHOICES, default='user'
    )
    email = models.EmailField('email address', unique=True)
    confirmation_code = models.CharField(max_length=50)
