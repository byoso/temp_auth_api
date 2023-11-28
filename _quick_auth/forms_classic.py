from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from .utils import gettext_lazy as _
from .models_email import EmailAddress

User = get_user_model()


class LoginForm(forms.Form):
    credential = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _('Username or email'), 'class': 'input'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': _('Password'), 'class': 'input'})
    )

    def clean(self):
        cleaned_data = self.cleaned_data
        credential = cleaned_data.get('credential')
        password = cleaned_data.get('password')
        if "@" in credential:
            user = User.objects.filter(email=credential).first()
        else:
            user = User.objects.filter(username=credential).first()
        if not user or not user.check_password(password):
            raise ValidationError(_('Wrong credentials.'))
        email = EmailAddress.objects.filter(user=user, email=user.email).first()
        if not email or not email.verified:
            raise ValidationError(
                _('Your email account has not been confirmed yet. Please confirm your email address before logging in.')
                )
        return cleaned_data

class SignupForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _('Username'), 'class': 'input'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': _('Email'), 'class': 'input'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': _('Password'), 'class': 'input'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': _('Password confirmation'), 'class': 'input'})
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError(_('This username is already taken.'))
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        validate_password(password)
        return password

    def clean_email(self):
        email = self.cleaned_data.get('email')
        return email

    def clean(self):
        cleaned_data = self.cleaned_data
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')
        if password != password2:
            raise ValidationError(_('Passwords do not match.'))
        return cleaned_data
