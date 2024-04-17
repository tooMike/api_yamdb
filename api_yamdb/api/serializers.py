from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.validators import UniqueValidator

from users.constants import CHOICES


User = get_user_model()


# Пишем собственный сериализатор для запросов на получение кода подтверждения,
# чтобы избежать проверки на уникальность пары username-email в БД
class UserAuthSerializer(serializers.Serializer):
    """Сериализатор для получения кода подтверждения."""

    username = serializers.SlugField(max_length=150)
    email = serializers.EmailField(max_length=254)

    def validate_username(self, value):
        """Проверка на недопустимое значение me."""
        if value == "me":
            raise serializers.ValidationError(
                "Недопустимое значение username: me"
            )
        return value

    def validate(self, data):
        """Проверяем допустимые значения полей."""
        username = data.get("username")
        email = data.get("email")

        # Проверяем существование пользователя с таким username
        user_by_username = User.objects.filter(username=username).first()

        # Проверяем существование пользователя с таким email
        user_by_email = User.objects.filter(email=email).first()

        if user_by_username:
            # Если пользователь с таким username найден, проверяем его email
            if user_by_username.email != email:
                raise ValidationError(
                    "Пользователь с этим username ",
                    "уже существует с другим email."
                )

        if not user_by_username and user_by_email:
            # Если username не занят, но email уже используется
            raise ValidationError("Этот email уже занят.")

        return data


class GetTokenSerializer(serializers.ModelSerializer):
    """Сериализатор для получения токена."""

    class Meta:
        model = User
        fields = ("username", "confirmation_code")

    def validate_username(self, value):
        """Проверяем допустимые значения поля username."""
        if not User.objects.filter(username=value).exists():
            raise NotFound("Username not found")
        return value

    def validate(self, data):
        try:
            confirmation_code = User.objects.get(username=data["username"])
            if confirmation_code.confirmation_code != data[
                "confirmation_code"
            ]:
                raise serializers.ValidationError("Переданы неверные данные")
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "Код подтверждения не найден для данного пользователя"
            )
        return data


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для работы админимстратора
    и суперюзера с пользователями.
    """

    username = serializers.SlugField(
        max_length=150, validators=[
            UniqueValidator(queryset=User.objects.all())
        ]
    )
    email = serializers.EmailField(
        max_length=254, validators=[
            UniqueValidator(queryset=User.objects.all())
        ]
    )
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    bio = serializers.CharField(required=False)
    role = serializers.ChoiceField(choices=CHOICES, required=False)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role"
        )

    def validate_username(self, value):
        """Проверяем на недопустимое значение username: me."""
        if value == "me":
            raise serializers.ValidationError(
                "Недопустимое значение username: me"
            )
        return value


class MeUserSerializer(UserSerializer):
    """
    Сериализатор для получения и редактирования
    пользователями информации и себе.
    """

    role = serializers.ChoiceField(
        choices=CHOICES,
        required=False,
        read_only=True
    )
