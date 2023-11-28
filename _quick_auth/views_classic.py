from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.views import View
from django.conf import settings

from .utils import (
    gettext_lazy as _,
    send_confirm_email,
)

from .config import QUICK_AUTH as conf
from .forms_classic import LoginForm, SignupForm
from .models_email import EmailAddress


User = get_user_model()
base_template = conf['BASE_TEMPLATE']
home_url = conf['HOME_URL']


class Login(View):
    template_name = 'auth/classic/login.html'

    def get(self, request):
        context = {
            'form': LoginForm(),
            'base_template': base_template,
            }
        return render(request, self.template_name, context)

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            credential = form.cleaned_data.get('credential')
            password = form.cleaned_data.get('password')
            if "@" in credential:
                user = User.objects.filter(email=credential).first()
            else:
                user = User.objects.filter(username=credential).first()
            user = authenticate(username=user.username, password=password)
            if user:
                login(request, user)
                if self.request.GET.get('next'):
                    return redirect(self.request.GET.get('next'))
                return redirect(home_url)

        context = {
            'form': form,
            'base_template': base_template,
            }

        return render(request, self.template_name, context)


class Logout(View):
    def post(self, request):
        logout(request)
        return redirect(home_url)


class Signup(View):
    def get(self, request):
        context = {
            'form': SignupForm(),
            'display': 'info',
            'base_template': base_template,
            }
        return render(request, 'auth/classic/signup.html', context)

    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            user = User.objects.create_user(username, email, password)
            user.save()

            new_email, _created = EmailAddress.objects.get_or_create(user=user, email=email)

            send_confirm_email(request, user, new_email.email)
            context = {
                'form': form,
                'base_template': base_template,
                'display': 'success',
                }
            return render(request, 'auth/classic/signup.html', context)

        context = {
            'form': form,
            'display': 'info',
            'base_template': base_template,
            }
        return render(request, 'auth/classic/signup.html', context)