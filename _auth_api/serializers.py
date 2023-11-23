from django.contrib.auth import get_user_model
from django.core import exceptions
from django.contrib.auth.password_validation import validate_password
from .utils import gettext_lazy as _

from rest_framework import serializers

from .models_email import EmailAddress
### WIP

User = get_user_model()


class UserInfosSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "is_superuser",
            "username",
            "email",
            "is_staff",
            "is_active",
            "groups",
            "user_permissions",
            # comment if not usefull:
            "first_name",
            "last_name",
            "last_login",
            "date_joined",
        ]

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


class LoginSerializer(serializers.Serializer):
    credential = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        credential = data.get('credential')
        password = data.get('password')
        errors = dict()

        if not credential or not password:
            raise serializers.ValidationError(_("Please enter both a username/email and a password."))

        if "@" in credential:
            email = EmailAddress.objects.filter(email=credential).first()
            if not email:
                errors['credential'] = _("Incorrect credentials.")
                user = None
            if not email.verified:
                errors['credential'] = _("This email address has not been confirmed yet. Please confirm your email address before logging in.")
                user = None
            else:
                user = email.user
        else:
            user = User.objects.filter(username=credential).first()
            if not user:
                errors['credential'] = _("Incorrect credentials.")
            if user:
                match = user.check_password(password)
            if match:
                email = EmailAddress.objects.filter(user=user, email=user.email).first()
                if not user.is_superuser and (not email or not email.verified):
                    msg = _(
                        'Your account is unconfirmed. '
                        'Please confirm your email account before logging in.')
                    raise serializers.ValidationError({'detail': [msg]}, code='authorization')

        if not user.check_password(password):
            errors['credential'] = _("Incorrect credentials.")

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
