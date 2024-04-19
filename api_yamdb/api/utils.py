import random
import string

from rest_framework_simplejwt.tokens import AccessToken

from users.constants import CONFIRMATION_CODE_LENGTH


def get_tokens_for_user(user):
    """Получаем токен для пользователя."""
    access = AccessToken.for_user(user)

    return {
        "token": str(access)
    }


def create_confirmation_code(
    size=CONFIRMATION_CODE_LENGTH,
    chars=string.ascii_uppercase + string.digits
):
    """Генерируем код подтверждения."""
    return "".join(random.choice(chars) for _ in range(size))
