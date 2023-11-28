from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views import View
from django.contrib.auth import authenticate

from django.contrib.auth import get_user_model
from django.contrib import messages

from .utils import gettext_lazy as _
from .utils import (
    read_jwt_token,
    send_confirm_email,
    send_password_reset_email,
    user_email_is_verified,
    )
from .models_email import EmailAddress
from .forms import ChangeEmailForm, PasswordResetForm

User = get_user_model()


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
            'new_one_link': reverse('change_email'),
        }
        return render(request, 'auth/confirm_email.html', context)

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
            obsolete_adresses = EmailAddress.objects.filter(email=email.email).exclude(user=user)
            obsolete_adresses.delete()
            display = 'success'
            username = user.username
        context = {
            'display': display,
            'username': username,
            'domain': request.get_host(),
            'please_confirm': please_confirm,
            'token': token,
        }
        return render(request, 'auth/confirm_email.html', context)


class ChangeEmailView(View):
    def get(self, request):
        form = ChangeEmailForm()
        context = {
            'form': form,
            'domain': request.get_host(),
            "display": "info",
        }
        return render(request, 'auth/change_email.html', context)

    def post(self, request):
        form = ChangeEmailForm(request.POST)

        if not form.is_valid():
            messages.add_message(
                request, messages.ERROR,
                _('Wrong credentials.'),
                extra_tags='danger'
                )
            context = {
                'form': form,
                'domain': request.get_host(),
                "display": 'info',
            }
            render(request, 'auth/change_email.html', context)
        username = form.cleaned_data['username']
        new_email = form.cleaned_data['email']
        user = authenticate(username=username, password=form.cleaned_data['password'])
        if user:
            user.email = new_email
            user.save()
            registrated_email, _created = EmailAddress.objects.get_or_create(user=user, email=new_email)
            if registrated_email.verified:
                registrated_email.primary = True
                registrated_email.save()
                display = 'success_no_confirm'
            else:
                send_confirm_email(request, user, new_email)
                display = 'success'
            context = {
                'form': form,
                'domain': request.get_host(),
                "display": display,
            }
            return render(request, 'auth/change_email.html', context)
        else:
            context = {
                'form': form,
                'domain': request.get_host(),
                "display": 'info',
            }
            return render(request, 'auth/change_email.html', context)



class PasswordResetRequest(View):
    def get(self, request):
        context = {
            'domain': request.get_host(),
            "display": "info",
        }
        return render(request, 'auth/password_reset_request.html', context)

    def post(self, request):
        credential = request.POST.get('credential')
        if "@" in credential:
            verified_email_address = EmailAddress.objects.filter(email=credential, verified=True).first()
            if verified_email_address:
                user = verified_email_address.user
            else:
                user = None
        else:
            user = User.objects.filter(username=credential).first()
            if user:
                verified_email_address = EmailAddress.objects.filter(user=user, verified=True).first()
            else:
                verified_email_address = None

        if not user:
            messages.add_message(
                request, messages.ERROR,
                _("No user found with the credential '%(credential)s'.") % {'credential': credential},
                extra_tags='danger'
                )
            return redirect('password_reset_request')

        if not verified_email_address:
            messages.add_message(
                request, messages.ERROR,
                _("The account '%(credential)s' has not been confirmed yet. Please confirm your email account first.") % {'credential': credential},
                extra_tags='danger'
                )
            return redirect('password_reset_request')

        send_password_reset_email(request, user)
        context = {
            'domain': request.get_host(),
            "display": "success",
        }
        return render(request, 'auth/password_reset_request.html', context)


class PasswordReset(View):
    def get(self, request, token):
        form = PasswordResetForm()
        token_content = read_jwt_token(token)
        user = token_content['user']
        action = token_content['action']
        if not user or action != 'reset_password':
            display = 'error'
            username = None
        else:
            display = 'info'
            username = user.username
        context = {
            'form': form,
            'display': display,
            'username': username,
            'domain': request.get_host(),
            'token': token,
            'new_one_link': reverse('password_reset_request'),
        }
        return render(request, 'auth/password_reset.html', context)

    def post(self, request, token):
        display = 'info'
        form = PasswordResetForm(request.POST)
        token_content = read_jwt_token(token)
        user = token_content['user']
        action = token_content['action']
        if not user or action != 'reset_password':
            display = 'error'
            username = None
        else:
            username = user.username
            password = request.POST.get('password')

            if form.is_valid():
                user.set_password(password)
                user.save()
                # if not already verified, the email is now verified and primary
                email = EmailAddress.objects.filter(user=user, email=user.email).first()
                email.verified = True
                email.primary = True
                email.save()
                display = 'success'
            else:
                for error in form.errors:
                    messages.add_message(
                        request, messages.ERROR,
                        form.errors[error],
                        extra_tags='danger'
                        )
                context = {
                    'form': form,
                    'display': display,
                    'username': username,
                    'domain': request.get_host(),
                    'token': token,
                    'new_one_link': reverse('password_reset_request'),
                }
                return render(request, 'auth/password_reset.html', context)
        display = 'success'
        context = {
            'display': display,
            'username': username,
            'domain': request.get_host(),
            'token': token,
            'new_one_link': reverse('password_reset_request'),
        }
        return render(request, 'auth/password_reset.html', context)