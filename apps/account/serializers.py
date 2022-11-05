import email
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate

from .tasks import send_activation_code



User = get_user_model()

def email_validator(email):
    if not User.objects.filter(email=email).exists():
        raise serializers.ValidationError(
            'User with this email does not exists'
        )
    return email

class UserRegistrationSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(max_length=128, required=True)

    class Meta:
        model = User 
        fields = ('username', 'email', 'password', 'password_confirm')

    def validate_username(self, username):
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                'This username is already taken, please choose another'
            )
        return username

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                'Email already in use'
            )
        return email

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.pop('password_confirm')
        if password != password_confirm:
            raise serializers.ValidationError('Passwords do not match')
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.create_activation_code()
        send_activation_code.delay(user.email, user.activation_code)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=128)

    def validate_username(self, username):
        if not User.objects.filter(username=username).exists():
            raise serializers.ValidationError('Пользователя с указанным ником не существует')
        return username
    
    def validate(self, attrs):
        # print('*' * 20, self.context)
        request = self.context.get('request')
        username = attrs.get('username')
        password = attrs.get('password')
        if username and password:
            user = authenticate(
                username=username,
                password=password,
                request=request
            )
            if not user:
                raise serializers.ValidationError('Неправильный username или пароль')
        else:
            raise serializers.ValidationError('Заполните все поля')
        attrs['user'] = user
        return attrs