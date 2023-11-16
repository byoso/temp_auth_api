from django.shortcuts import render
from django.views import View

from django.contrib.auth import get_user_model
from django.contrib import messages

from .utils import gettext_lazy as _
from .utils import read_jwt_token

User = get_user_model()

# WIP

# confirm email / change email
# reset password

class ConfirmEmail(View):
    def get(self, request, token):
        token_content = read_jwt_token(token)
        user = token_content['user']
        action = token_content['action']
        please_confirm = True
        if not user or action != 'confirm_email':
            display = 'error'
            please_confirm = False
            username = None
        else:
            display = 'info'
            username = user.username
        context = {
            'display': display,
            'username': username,
            'domain': request.get_host(),
            'please_confirm': please_confirm,
            'token': token,
        }
        return render(request, '_auth_api/confirm_email.html', context)

    def post(self, request, token):
        token_content = read_jwt_token(token)
        user = token_content['user']
        action = token_content['action']
        display = 'info'
        username = user.username
        please_confirm = False
        if not user or action != 'confirm_email':
            display = 'error'
            please_confirm = False
            username = None
        else:
            # confirmaiton logic here
            print("===POST !")
            display = 'success'
            username = user.username
        context = {
            'display': display,
            'username': username,
            'domain': request.get_host(),
            'please_confirm': please_confirm,
            'token': token,
        }
        return render(request, '_auth_api/confirm_email.html', context)