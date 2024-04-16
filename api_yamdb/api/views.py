import random
import string

from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from api.serializers import UserAuthSerializer, GetTokenSerializer


User = get_user_model()

# Получаем токен для пользователя
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# Генерируем код подтверждения
def create_confirmation_code(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


@api_view(['POST'])
def user_signup(request):
    data = request.data
    serializer = UserAuthSerializer(data=data)
    if serializer.is_valid():
        try:
            user = User.objects.get(**serializer.validated_data)
            confirmation_code = user.confirmation_code
        except User.DoesNotExist:
            confirmation_code = create_confirmation_code()
            # user = serializer.save(confirmation_code=confirmation_code)
            user = User.objects.create(
                **serializer.validated_data,
                confirmation_code=confirmation_code
            )
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Отправка письма с кодом подтверждения
    send_mail(
        subject='Тема письма',
        message=f'Код подтверждения: {confirmation_code}',
        from_email='from@example.com',
        recipient_list=[user.email],
        fail_silently=True,
    )
    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['POST'])
def get_token(request):
    serializer = GetTokenSerializer(data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
    except NotFound as e:
        return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    user = serializer.validated_data['user']
    token = get_tokens_for_user(user)
    return Response(token, status=status.HTTP_200_OK)
    
