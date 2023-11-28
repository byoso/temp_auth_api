from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from .utils import gettext_lazy as _


User = get_user_model()


class ChangeEmailForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _('Username or email'), 'class': 'input'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': _('Password'), 'class': 'input'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': _('New email'), 'class': 'input'})
    )

    def clean(self):
        cleaned_data = self.cleaned_data
        password = cleaned_data.get('password')
        username = cleaned_data.get('username')
        user = User.objects.filter(username=username).first()
        if not user or not user.check_password(password):
            raise forms.ValidationError(_('Wrong credentials.'))
        return cleaned_data


class PasswordResetForm(forms.Form):
    password = forms.CharField()
    password2 = forms.CharField()

    def clean_password2(self):
        cleaned_data = self.cleaned_data
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')
        if password and password != password2:
            raise forms.ValidationError(_('The passwords you entered do not match.'))
        return cleaned_data

    def clean_password(self):
        password = self.cleaned_data['password']
        validate_password(password)
        return password
