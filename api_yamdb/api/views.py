from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.filters import TitleFilter
from api.mixins import GetListCreateDeleteViewSet
from api.permissions import (IsAdminModeratorAuthorReadOnly, IsAdminOrReadOnly,
                             IsSuperUserOrIsAdmin)
from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, GetTokenSerializer,
                             MeUserSerializer, ReviewSerializer,
                             TitleSerializer, UserAuthSerializer,
                             UserSerializer)
from api.user_auth_utils import get_tokens_for_user
from reviews.models import Category, Genre, Review, Title

User = get_user_model()


@api_view(["POST"])
@permission_classes([AllowAny])
def user_signup(request):
    """Представление для получения кода подтверждения."""
    data = request.data
    serializer = UserAuthSerializer(data=data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def get_token(request):
    """Представление для получения токена."""
    serializer = GetTokenSerializer(data=request.data)
    if serializer.is_valid():
        user = get_object_or_404(
            User,
            username=serializer.validated_data["username"]
        )
        token = get_tokens_for_user(user)
        return Response(token, status=status.HTTP_200_OK)
    return Response(
        "Ошибка: введены неверные данные",
        status=status.HTTP_400_BAD_REQUEST
    )


class UsersViewSet(viewsets.ModelViewSet):
    """
    Представление для работы админимстратора
    и суперюзера с пользователями.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsSuperUserOrIsAdmin,)
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ("username",)
    lookup_field = "username"
    http_method_names = ("get", "post", "patch", "delete")

    def get_permissions(self):
        """
        Задаем разные разрешения для эндпоинта me и остальных эндпоинтов.
        """
        if self.action == 'me':
            return (IsAuthenticated(),)
        return super().get_permissions()

    def get_serializer_class(self):
        """
        Задаем разные сериализаторы для эндпоинта me и остальных эндпоинтов.
        """
        if self.action == 'me':
            return MeUserSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=("get", "patch", "delete", "post"))
    def me(self, request):
        """
        Метод для просмотра и редактирования пользователем информации о себе.
        """
        # Задаем явный вызов ошибок при методах DELETE и POST потому что
        # иначе возвращается 403 ошибка, а тесты ожидают 405, т.е. более
        # логичный вариант изменить список разрешенных методов не работает
        if request.method in ('DELETE', 'POST'):
            return Response({"Метод не разрешен."},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        user = self.request.user
        serializer = self.get_serializer(user)
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                user, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
        return Response(serializer.data)


class CategoryViewSet(GetListCreateDeleteViewSet):
    """Получение списка всех категорий."""

    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer


class GenreViewSet(GetListCreateDeleteViewSet):
    """Получение списка всех жанров."""

    queryset = Genre.objects.all().order_by('name')
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """Получение списка всех произведений."""

    queryset = Title.objects.all().annotate(
        rating=Avg('reviews__score')
    ).order_by('-year')
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    http_method_names = ("get", "post", "patch", "delete")


class ReviewViewSet(viewsets.ModelViewSet):
    """Обзоры viewset."""

    serializer_class = ReviewSerializer
    permission_classes = (IsAdminModeratorAuthorReadOnly,)
    http_method_names = ("get", "post", "patch", "delete")

    def get_title(self):
        """Получаем соответствующий Title."""
        return get_object_or_404(
            Title,
            id=self.kwargs.get('title_id')
        )

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """Комментарии viewset."""

    serializer_class = CommentSerializer
    permission_classes = (IsAdminModeratorAuthorReadOnly,)
    http_method_names = ("get", "post", "patch", "delete")

    def get_review(self):
        return get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title=self.kwargs.get('title_id')
        )

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
