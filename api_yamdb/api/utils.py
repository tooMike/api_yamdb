import random
import string

from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(user):
    """Получаем токен для пользователя."""
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def create_confirmation_code(
    size=settings.CONFIRMATION_CODE_LENGTH,
    chars=string.ascii_uppercase + string.digits
):
    """Генерируем код подтверждения."""
    return "".join(random.choice(chars) for _ in range(size))
