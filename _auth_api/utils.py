from threading import Thread
from time import time

from django.utils.translation import gettext_lazy
from django.conf import settings
from django.shortcuts import reverse, get_object_or_404
from django.core.mail import send_mail
from django.template.loader import get_template
from django.contrib.auth import get_user_model

import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError

from .config import _AUTH_API as conf
from .models_email import EmailAddress

User = get_user_model()

SITE_NAME = conf['SITE_NAME']
EMAIL_VALID_TIME = conf['EMAIL_VALID_TIME']
PREFIX = conf['URL_PREFIX']

# in django.utils.translation:
# gettext_lazy = lazy(gettext, str)

if settings.USE_I18N:
    gettext_lazy = gettext_lazy
else:
    def gettext_lazy(string):
        """So there will be no migration errors with or without i18n.
        """
        return string


def write_jwt_token(user, expires_in=EMAIL_VALID_TIME, action="unspecified"):

    token = jwt.encode(
        {'id': str(user.id), 'exp': time()+expires_in, 'action': action},
        settings.SECRET_KEY, algorithm='HS256'
    )
    return token


def read_jwt_token(token):
    try:
        pk = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=['HS256'])['id']
        action = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=['HS256'])['action']
    except (ExpiredSignatureError, InvalidSignatureError):  # invalid token
        jwt_content = {'user': None, 'action': None}
        return jwt_content
    user = User.objects.filter(id=pk).first()
    if not user:
        user = None
    jwt_content = {'user': user, 'action': action}
    return jwt_content


def dsa_send_mail(*args, **kwargs):
    send = Thread(target=send_mail, args=args, kwargs=kwargs, daemon=True)
    send.start()


def send_password_reset_email(request, user):
    token = write_jwt_token(user, expires_in=EMAIL_VALID_TIME, action="reset_password")
    domain = request.get_host()
    link = f"http://{domain}/{PREFIX}password_reset/{token}"
    context = {
        'user': user,
        'link': link,
        'site_name': SITE_NAME or request.get_host()
    }

    msg_text = get_template("_auth_api/emails/request_password_reset.txt")

    dsa_send_mail(
        'Password reset request',
        msg_text.render(context),
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )


def send_confirm_email(request, user, email=None):
    if email == None:
        raise ValueError("email must be provided")
    token = write_jwt_token(user, expires_in=EMAIL_VALID_TIME, action="confirm_email")
    domain = request.get_host()
    link = f"http://{domain}/{PREFIX}confirm_email/{token}"
    context = {
        'user': user,
        'link': link,
        'site_name': SITE_NAME,
    }

    msg_text = get_template("_auth_api/emails/confirm_email.txt")


    dsa_send_mail(
        'Confirm your new email',
        msg_text.render(context),
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )


def user_email_is_verified(user, email):
    verified_email = EmailAddress.objects.filter(user=user, email=email, verified=True).first()
    if verified_email:
        return True
    return False
