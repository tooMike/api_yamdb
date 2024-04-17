from django.contrib.auth.models import AbstractUser
from django.db import models


from users.constants import CHOICES


class MyUser(AbstractUser):
    username = models.SlugField(max_length=150, unique=True,)
    bio = models.TextField('Биография', blank=True)
    role = models.CharField(
        'Роль', max_length=50, choices=CHOICES, default='user'
    )
    email = models.EmailField('email address', unique=True)
    confirmation_code = models.CharField(max_length=50)
