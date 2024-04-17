from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework import filters, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import NotFound
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.permissions import AdminOnlyPermission
from api.serializers import (GetTokenSerializer, MeUserSerializer,
                             UserAuthSerializer, UserSerializer)
from api.utils import get_tokens_for_user, create_confirmation_code


User = get_user_model()


@api_view(["POST"])
@permission_classes([AllowAny])
def user_signup(request):
    """Представление для получения кода подтверждения."""
    data = request.data
    serializer = UserAuthSerializer(data=data)
    if serializer.is_valid():
        try:
            user = User.objects.get(**serializer.validated_data)
            confirmation_code = user.confirmation_code
        except User.DoesNotExist:
            confirmation_code = create_confirmation_code()
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
    user = serializer.validated_data["user"]
    token = get_tokens_for_user(user)
    return Response(token, status=status.HTTP_200_OK)


class UsersViewSet(viewsets.ModelViewSet):
    """
    Представление для работы админимстратора
    и суперюзера с пользователями.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AdminOnlyPermission,)
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ("username",)
    lookup_field = "username"
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]


class MeUserViewSet(viewsets.ModelViewSet):
    """
    Представление для получения и редактирования
    пользователями информации и себе.
    """

    queryset = User.objects.all()
    serializer_class = MeUserSerializer
    http_method_names = ["get", "patch", "head", "options"]

    def get_object(self):
        """Получить объект текущего пользователя."""
        return self.request.user
