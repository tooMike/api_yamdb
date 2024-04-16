from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from django.core.exceptions import ValidationError

username_validator = RegexValidator(
    regex=r'^[\w.@+-]+\Z',
    message="Invalid characters in username. Only alphanumeric and .@+-_ characters are allowed."
)



User = get_user_model()

# class UserAuthSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = User
#         fields = ('email', 'username')

#     def validate(self, data):
#         if data['username'] == 'me':
#             raise serializers.ValidationError('Недопустимое значение username')
#         return data

class UserAuthSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150,
        validators=[username_validator]
    )
    email = serializers.EmailField(max_length=254)

    def validate_username(self, value):
        # Проверка на специфическое недопустимое значение
        if value == 'me':
            raise serializers.ValidationError('Недопустимое значение username: "me"')
        return value
    
    def validate(self, data):
        username = data.get('username')
        email = data.get('email')

        # Проверяем существование пользователя с таким username
        user_by_username = User.objects.filter(username=username).first()

        # Проверяем существование пользователя с таким email
        user_by_email = User.objects.filter(email=email).first()

        if user_by_username:
            # Если пользователь с таким username найден, проверяем его email
            if user_by_username.email != email:
                raise ValidationError("Пользователь с данным username уже существует с другим email.")

        if not user_by_username and user_by_email:
            # Если username не занят, но email уже используется
            raise ValidationError("Этот email уже занят.")

        return data

        
        



class GetTokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')

    def validate_username(self, value):
        if not User.objects.filter(username=value).exists():
            raise NotFound('Username not found')
        return value
        
    def validate(self, data):
        try:
            confirmation_code = User.objects.get(username=data['username'])
            if confirmation_code.confirmation_code != data['confirmation_code']:
                raise serializers.ValidationError('Переданы неверные данные')
        except User.DoesNotExist:
            raise serializers.ValidationError('Код подтверждения не найден для данного пользователя')
        return data

    

