from django.contrib.auth import get_user_model
from django.core import exceptions
from django.contrib.auth.password_validation import validate_password
from .utils import gettext_lazy as _

from rest_framework import serializers

### WIP

User = get_user_model()


class UserInfosSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password', ]


class GetAllUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class SignupSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()
    password2 = serializers.CharField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'password2')

    def validate_username(self, value):
        username = value
        errors = dict()
        username_errors = list()

        if User.objects.filter(username=username).exists():
            username_errors += [_("This username is already associated with an existing account."), ]

        if "@" in username:
            username_errors += [_("A username cannot include the symbol '@'."), ]

        if username_errors:
            errors = username_errors
            raise serializers.ValidationError(errors)
        return value

    def validate_password(self, value):
        try:
            validate_password(value)
        except serializers.ValidationError as exc:
            raise serializers.ValidationError(str(exc))
        return value

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError(_("The passwords you entered do not match."))
        return data



class PasswordsSerializer(serializers.Serializer):
    password = serializers.CharField(
        write_only=True
    )
    password2 = serializers.CharField(
        write_only=True
    )

    def validate(self, data):
        password = data.get('password')
        password2 = data.get('password2')
        errors = dict()
        password_errors = list()

        if password != password2:
            password_errors += [_("The passwords you entered do not match."), ]

        try:
            validate_password(
                password=password,
                user=None,
                password_validators=None)

        except exceptions.ValidationError as e:
            password_errors += list(e.messages)

        if password_errors:
            errors['password'] = password_errors
            raise serializers.ValidationError(errors)
        return data


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        email = data.get('email')
        errors = dict()
        email_errors = list()

        if User.objects.filter(email=email).exists():
            email_errors += [_("This email is already associated with an existing account."), ]

        if email_errors:
            errors['email'] = email_errors
            raise serializers.ValidationError(errors)
        return data


class LoginSerializer(serializers.Serializer):
    credential = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        credential = data.get('credential')
        password = data.get('password')
        errors = dict()

        if "@" in credential:
            if not User.objects.filter(email=credential).exists():
                errors['detail'] = _("Incorrect credentials.")
        else:
            if not User.objects.filter(username=credential).exists():
                errors['detail'] = _("Incorrect credentials.")

        if errors:
            raise serializers.ValidationError(errors)
        return data


class UsernameSerializer(serializers.Serializer):
    username = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        errors = dict()
        username_errors = list()

        if User.objects.filter(username=username).exists():
            username_errors += [_("This username is already associated with an existing account."), ]

        if "@" in username:
            username_errors += [_("A username cannot include the symbol '@'."), ]

        if username_errors:
            errors['username'] = username_errors
            raise serializers.ValidationError(errors)
        return data
