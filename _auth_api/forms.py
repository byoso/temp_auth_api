from django import forms
from django.contrib.auth import get_user_model


class ChangeEmailForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['username', 'password', 'email',]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        username = cleaned_data.get('username')
        self.instance = get_user_model().objects.filter(username=username).first()
        print("==== instance: ", self.instance)
        if not self.instance or not self.instance.check_password(password):
            raise forms.ValidationError('Wrong credentials.')
        return cleaned_data