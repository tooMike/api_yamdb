from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from reviews.validators import validate_year


User = get_user_model()


class BasePost(models.Model):
    """Базовая абстрактная модель для наследования в ревью и комментариях."""
    author = models.ForeignKey(
        to=User, on_delete=models.CASCADE, verbose_name='Автор'
    )
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Опубликовано', auto_now_add=True
    )
    edited_date = models.DateTimeField(verbose_name='Изменено', auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.text[:settings.CUT_STR_LONGER]


class ModelForCategoryGenre(models.Model):
    """Базовая абстрактная модель для наследования в категориях и жанрах."""
    name = models.CharField(max_length=256, verbose_name='Имя')
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Review(BasePost):
    """Модель Ревью"""
    title = models.ForeignKey(
        to='Title',
        verbose_name='Произведение',
        on_delete=models.CASCADE,
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        validators=[
            MaxValueValidator(
                limit_value=10, message='Оценка не может быть больше 10 баллов'
            ),
            MinValueValidator(
                limit_value=1, message='Оценка не может быть меньше 1го балла'
            )
        ]
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['title', 'author'],
            name='Only_one_review_from_author_for_title'
        )]
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'
        default_related_name = 'reviews'
        ordering = ('pub_date',)


class Comment(BasePost):
    """Модель комментариев"""
    review = models.ForeignKey(
        to=Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв',
        related_name='comments'
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'
        ordering = ('pub_date',)


class Category(ModelForCategoryGenre):
    """Модель категорий"""
    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Genre(ModelForCategoryGenre):
    """Модель жанров"""
    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    """Модель произведений"""
    name = models.CharField(max_length=256, verbose_name='Имя')
    year = models.PositiveSmallIntegerField(
        validators=[validate_year],
        verbose_name='Год'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='Описание'
    )
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        verbose_name='Жанр'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
        verbose_name='Категория'
    )

    class Meta:
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    """Модель для связи произведений и жанров"""
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.genre} {self.title}'
