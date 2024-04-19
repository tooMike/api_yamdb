from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from api.utils import create_confirmation_code
from reviews.models import Category, Comment, Genre, Review, Title
from users.constants import Roles
from users.validators import username_validator

User = get_user_model()


# Пишем собственный сериализатор для запросов на получение кода подтверждения,
# чтобы избежать проверки на уникальность пары username-email в БД
class UserAuthSerializer(serializers.Serializer):
    """Сериализатор для получения кода подтверждения."""

    username = serializers.CharField(
        max_length=150,
        validators=(username_validator,)
    )
    email = serializers.EmailField(max_length=254)

    def validate(self, data):
        """Проверяем допустимые значения полей."""
        username = data.get("username")
        email = data.get("email")

        # Проверяем существование пользователя с таким username
        user_by_username = User.objects.filter(username=username).first()

        # Проверяем существование пользователя с таким email
        user_by_email = User.objects.filter(email=email).first()

        errors = {}
        if user_by_username:
            # Если пользователь с таким username найден, проверяем его email
            if user_by_username.email != email:
                errors['username'] = ("Пользователь с этим username "
                                      "уже существует с другим email.")
                # Проверяем дополнительно, занят ли переданный email
                if user_by_email:
                    errors['email'] = "Этот email уже занят."

        if not user_by_username and user_by_email:
            errors['email'] = "Этот email уже занят."

        if errors:
            raise ValidationError(errors)

        return data

    def create(self, validated_data):
        confirmation_code = create_confirmation_code()
        user, created = User.objects.get_or_create(**validated_data)
        user.confirmation_code = confirmation_code
        user.save()

        send_mail(
            subject="Регистрация в YaMDB",
            message=f"Код подтверждения: {confirmation_code}",
            from_email="from@example.com",
            recipient_list=(user.email,),
            fail_silently=True,
        )
        return user


class GetTokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена."""

    username = serializers.CharField(
        max_length=150,
        validators=(username_validator,)
    )
    confirmation_code = serializers.CharField(max_length=50)

    def validate(self, data):
        user = get_object_or_404(User, username=data["username"])
        if user.confirmation_code != data["confirmation_code"]:
            raise serializers.ValidationError("Переданы неверные данные")
        return data


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для работы админимстратора
    и суперюзера с пользователями.
    """

    class Meta:
        model = User
        fields = ("username", "email", "first_name",
                  "last_name", "bio", "role")


class MeUserSerializer(UserSerializer):
    """
    Сериализатор для получения и редактирования
    пользователями информации и себе.
    """

    role = serializers.ChoiceField(
        choices=Roles.choices, required=False, read_only=True)


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категорий."""

    class Meta:
        model = Category
        fields = ("name", "slug")
        lookup_field = "slug"


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор жанров."""

    class Meta:
        model = Genre
        fields = ("name", "slug")
        lookup_field = "slug"


class DictSlugRelatedField(SlugRelatedField):
    """Способ отображения для Жанра и Категории в Произведении."""

    def to_representation(self, obj):
        result = {"name": obj.name, "slug": obj.slug}
        return result


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор произведений для отображения."""

    category = DictSlugRelatedField(
        queryset=Category.objects.all(),
        slug_field="slug",
    )
    genre = DictSlugRelatedField(
        queryset=Genre.objects.all(),
        many=True,
        slug_field="slug",
    )
    rating = serializers.IntegerField(
        read_only=True,
        default=None
    )
    # Добавляю значение по умолчанию, потому что запрос в Postman
    # ожидает, что значение этого поля будет string, а не Null,
    # хотя по ТЗ это поле не обязательное
    # description = serializers.CharField(
    #     default="Описание отсутствует"
    # )

    class Meta:
        model = Title
        fields = ("id", "name", "year", "rating",
                  "description", "genre", "category")

    def validate_genre(self, value):
        """Проверяем что в поле genre передано значение"""
        if not value:
            raise serializers.ValidationError(
                "Поле жанра не должно быть пустым"
            )
        return value


class ReviewSerializer(serializers.ModelSerializer):
    """Отзывы serializers."""

    author = serializers.SlugRelatedField(
        slug_field="username",
        default=serializers.CurrentUserDefault(),
        read_only=True,
    )

    def validate(self, data):
        if self.context.get("request").method == "POST":
            author = self.context.get("request").user
            title_id = self.context.get("view").kwargs.get("title_id")
            if Review.objects.filter(
                    author=author,
                    title__id=title_id
            ).exists():
                raise serializers.ValidationError(
                    "Можно написать только один обзор к произведению"
                )
        return data

    class Meta:
        model = Review
        fields = ("id", "text", "author", "score", "pub_date",)


class CommentSerializer(serializers.ModelSerializer):
    """Комментарии serializer."""

    author = serializers.SlugRelatedField(
        slug_field="username",
        default=serializers.CurrentUserDefault(),
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = ("id", "text", "author", "pub_date")
