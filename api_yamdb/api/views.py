from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import NotFound
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.filters import TitleFilter
from api.mixins import GetListCreateDeleteViewSet, GetPatchCreateDeleteViewSet
from api.permissions import (IsAdminModeratorAuthorReadOnly, IsAdminOrReadOnly,
                             IsSuperUserOrIsAdmin)
from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, GetTokenSerializer,
                             MeUserSerializer, ReviewSerializer,
                             TitleSerializer, UserAuthSerializer,
                             UserSerializer)
from api.utils import create_confirmation_code, get_tokens_for_user
from reviews.models import Category, Genre, Review, Title


User = get_user_model()


@api_view(["POST"])
@permission_classes([AllowAny])
def user_signup(request):
    """Представление для получения кода подтверждения."""
    data = request.data
    serializer = UserAuthSerializer(data=data)
    if serializer.is_valid():
        confirmation_code = create_confirmation_code()
        try:
            user = User.objects.get(**serializer.validated_data)
            user.confirmation_code = confirmation_code
            user.save()
        except User.DoesNotExist:
            user = User.objects.create(
                **serializer.validated_data,
                confirmation_code=confirmation_code
            )
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Отправка письма с кодом подтверждения
    send_mail(
        subject="Тема письма",
        message=f"Код подтверждения: {confirmation_code}",
        from_email="from@example.com",
        recipient_list=[user.email],
        fail_silently=True,
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def get_token(request):
    """Представление для получения токена."""
    serializer = GetTokenSerializer(data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
    except NotFound as e:
        return Response({"Ошибка": str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"Ошибка": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.get(username=serializer.validated_data["username"])
    token = get_tokens_for_user(user)
    return Response(token, status=status.HTTP_200_OK)


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
    http_method_names = ["get", "post", "patch", "delete"]


class MeUserViewSet(viewsets.ModelViewSet):
    """
    Представление для получения и редактирования
    пользователями информации и себе.
    """

    queryset = User.objects.all()
    serializer_class = MeUserSerializer
    http_method_names = ["get", "patch"]

    def get_object(self):
        """Получить объект текущего пользователя."""
        return self.request.user


class CategoryViewSet(GetListCreateDeleteViewSet):
    """Получение списка всех категорий."""

    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)


class GenreViewSet(GetListCreateDeleteViewSet):
    """Получение списка всех жанров."""

    queryset = Genre.objects.all().order_by('name')
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)


class TitleViewSet(GetPatchCreateDeleteViewSet):
    """Получение списка всех произведений."""

    queryset = Title.objects.all().annotate(
        Avg('reviews__score')
    ).order_by('-year')
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter


class ReviewViewSet(GetPatchCreateDeleteViewSet):
    """Обзоры viewset."""

    serializer_class = ReviewSerializer
    permission_classes = (IsAdminModeratorAuthorReadOnly,)

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


class CommentViewSet(GetPatchCreateDeleteViewSet):
    """Комментарии viewset."""

    serializer_class = CommentSerializer
    permission_classes = (IsAdminModeratorAuthorReadOnly,)

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
