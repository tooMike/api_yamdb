from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import NotFound



User = get_user_model()

class UserAuthSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'username')

    def validate(self, data):
        if data['username'] == 'me':
            raise serializers.ValidationError('Недопустимое значение username')
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

    

