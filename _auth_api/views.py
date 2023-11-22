from django.shortcuts import render, get_object_or_404, redirect
from django.views import View

from django.contrib.auth import get_user_model
from django.contrib import messages

from .utils import gettext_lazy as _
from .utils import read_jwt_token, send_confirm_email
from .models_email import EmailAddress
from .forms import ChangeEmailForm

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
            email = get_object_or_404(EmailAddress, user=user, email=user.email)
            email.verified = True
            email.primary = True
            email.save()
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


class ChangeEmailView(View):
    def get(self, request):
        form = ChangeEmailForm()
        context = {
            'form': form,
            'domain': request.get_host(),
            "display": "info",
        }
        return render(request, '_auth_api/change_email.html', context)

    def post(self, request):
        form = ChangeEmailForm(request.POST)
        if not form.is_valid():
            messages.add_message(
                request, messages.ERROR,
                _('Wrong credentials.'),
                extra_tags='danger'
                )
            return redirect('change_email')
        username = form.cleaned_data['username']
        new_email = form.cleaned_data['email']
        user = get_object_or_404(User, username=username)
        user.email = new_email
        user.save()
        EmailAddress.objects.get_or_create(user=user, email=new_email)
        send_confirm_email(request, user)
        display = 'success'
        context = {
            'form': form,
            'domain': request.get_host(),
            "display": display,
        }
        return render(request, '_auth_api/change_email.html', context)