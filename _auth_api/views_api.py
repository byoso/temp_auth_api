
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.http import Http404

from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.serializers import ValidationError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated

from .utils import (
    gettext_lazy as _,
    send_confirm_email,
    send_password_reset_email,
)

from .serializers import (
    LoginSerializer,
    SignupSerializer,
    UserInfosSerializer,
    GetAllUsersSerializer,
    PasswordsSerializer,
    EmailSerializer,
    UsernameSerializer,
    )

from .models_email import EmailAddress

# WIP
# reset password

User = get_user_model()


class Signup(APIView):
    permission_classes = []

    @transaction.atomic
    def post(self, request, format=None):
        """Create a new user"""
        serializer = SignupSerializer(data=request.data)
        message = ""
        if serializer.is_valid():
            user = User.objects.create(
                username=request.data['username'],
                email=request.data['email'],
            )
            user.set_password(request.data['password'])
            user.save()
            if not EmailAddress.objects.filter(user=user, email=user.email).exists():
                EmailAddress.objects.create(
                    user=user,
                    email=user.email,
                    verified=False,
                    primary=True
                )
            message = _(
                "Please check your inbox at '%(email)s' to confirm your account. "
                ) % {'email': user.email}

            serializer = UserInfosSerializer(user)
            msg = {
                "user": serializer.data,
                "message": message,
            }

            send_confirm_email(request, user)

            return Response(msg)
        else:
            error = serializer.errors
            raise ValidationError(error, code='authorization')


class LoginWithAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        """Login view modified to use email or username as credential"""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        credential = serializer.validated_data['credential']
        if "@" in credential:
            user = User.objects.filter(email=credential).first()
        else:
            user = User.objects.filter(username=credential).first()
        password = serializer.validated_data['password']
        match = False
        if user:
            match = user.check_password(password)
        if match:
            email = EmailAddress.objects.filter(user=user, email=user.email).first()
            if not email and not user.is_superuser:
                raise Http404
            if not user.is_superuser:
                if not email.verified:
                    msg = _(
                        'Your account has not been confirmed yet. '
                        'Please check your inbox for a confirmation link.')
                    raise ValidationError({'detail': [msg]}, code='authorization')
            token, created = Token.objects.get_or_create(user=user)
            if hasattr(user, 'last_login'):
                user.last_login = timezone.now()
                user.save()
            serializer = UserInfosSerializer(user)
            data = {
                'auth_token': token.key,
                'user': serializer.data
            }
            return Response(
                data,
                )
        msg = _('Incorrect credentials.')
        raise ValidationError({'detail': [msg]}, code='authorization')


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def token_logout(request):
    """Destroys the auth token"""
    request.user.auth_token.delete()
    return Response({'success': _('Logged out.')})


# @transaction.atomic
# @api_view(['POST'])
# @permission_classes([AllowAny])
# def email_confirm_email_resend(request):
#     """Resends an email to the user to confirm his account"""
#     credential = request.data.get('credential')
#     if not credential:
#         error = _("no credential provided")
#         raise ValidationError({"detail": [error]}, code='authorization')
#     if "@" in credential:
#         user = User.objects.filter(email=credential).first()
#     else:
#         user = User.objects.filter(username=credential).first()
#     user_email = get_object_or_404(EmailAddress, user=user, email=user.email)
#     if user_email:
#         if user_email.verified:
#             error = _("Your account is already confirmed.")
#             raise ValidationError({"detail": [error]}, code='authorization')
#         send_confirm_email(request, user)
#         return Response({'success': _('Email sent for password reset')})
#     error = "Invalid credential"
#     raise ValidationError({"detail": [error]}, code='authorization')


# @transaction.atomic
# @api_view(['POST'])
# @permission_classes([AllowAny])
# def password_request_reset(request):
#     """Sends an email to the user with a link to reset their password"""
#     credential = request.data.get('credential')
#     if not credential:
#         error = _("No credentials were provided")
#         raise ValidationError({"detail": [error]}, code='authorization')
#     if "@" in credential:
#         user = User.objects.filter(email=credential).first()
#     else:
#         user = User.objects.filter(username=credential).first()
#     if user:
#         send_password_reset_email(request, user)
#         return Response({'success': _("Email sent for password reset")})
#     error = _("Invalid credential")
#     raise ValidationError({"detail": [error]}, code='authorization')



@api_view(['GET'])
def get_users_all(request):
    """!! FOR DEV ONLY !! Get all users"""
    users = User.objects.all()
    serializer = GetAllUsersSerializer(users, many=True)
    return Response(serializer.data)


# @transaction.atomic
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def password_change(request):
#     """Changes the user's password"""
#     serializer = PasswordsSerializer(data=request.data)
#     if serializer.is_valid():
#         user = request.user
#         password = request.data.get('password')
#         user.set_password(password)
#         user.save()
#         return Response({'success': _('Password successfully changed.')})
#     error = serializer.errors
#     raise ValidationError(error, code='authorization')


# @transaction.atomic
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def email_request_change(request):
#     user = request.user
#     serializer = EmailSerializer(data=request.data)
#     if serializer.is_valid():
#         new_email = request.data.get('email')
#         user.new_email = new_email
#         user.save()
#         send_confirm_email(request, user, new_email=True)

#         return Response(
#             {'success': _(
#                 "New email saved, check your inbox at '%(new_email)s' "
#                 "to activate it."
#             ) % {'new_email': new_email}}
#         )
#     error = serializer.errors
#     raise ValidationError(error, code='authorization')


# @transaction.atomic
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def username_change(request):
#     """Changes the user's username"""
#     serializer = UsernameSerializer(data=request.data)
#     if serializer.is_valid():
#         user = request.user
#         username = request.data.get('username')
#         user.username = username
#         user.save()
#         return Response({'success': _('Username successfully changed.')})
#     error = serializer.errors
#     raise ValidationError(error, code='authorization')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def users_my_infos(request):
    """Returns the user's infos"""
    serializer = UserInfosSerializer(request.user)
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def users_delete_me(request):
    """Deletes the user's account"""
    request.user.auth_token.delete()
    request.user.delete()
    return Response({'success': _('Account successfully deleted.')})
