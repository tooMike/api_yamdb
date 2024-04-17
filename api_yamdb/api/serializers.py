from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.validators import UniqueValidator

from rest_framework.relations import SlugRelatedField

from reviews.models import Category, Comment, Genre, Review, Title

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

class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категорий."""

    class Meta:
        model = Category
        fields = ('name', 'slug',)
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор жанров."""

    class Meta:
        model = Genre
        fields = ('name', 'slug',)
        lookup_field = 'slug'


class DictSlugRelatedField(SlugRelatedField):
    """Способ отображения для Жанра и Категории в Произведении."""

    def to_representation(self, obj):
        result = {
            'name': obj.name,
            'slug': obj.slug
        }
        return result


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор произведений для отображения."""

    category = DictSlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug',
    )
    genre = DictSlugRelatedField(
        queryset=Genre.objects.all(),
        many=True,
        slug_field='slug',
    )
    rating = serializers.IntegerField(
        source='reviews__score__avg',
        read_only=True,
    )

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category'
        )


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор произведений для создания."""

    category = DictSlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug',
    )
    genre = DictSlugRelatedField(
        queryset=Genre.objects.all(),
        many=True,
        slug_field='slug',
    )

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category'
        )
        read_only_fields = ('rating',)


class ReviewSerializer(serializers.ModelSerializer):
    """Отзывы serializers."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        default=serializers.CurrentUserDefault(),
        read_only=True,
    )

    def validate(self, data):
        author = self.context.get('request').user
        title_id = self.context.get('view').kwargs.get('title_id')
        if (
            self.context.get('request').method == 'POST'
            and Review.objects.filter(
                author=author,
                title__id=title_id
            ).exists()
        ):
            raise serializers.ValidationError(
                'Можно написать только один обзор к произведению'
            )
        return data

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date',)


class CommentSerializer(serializers.ModelSerializer):
    """Комментарии serializer."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        default=serializers.CurrentUserDefault(),
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date',)
