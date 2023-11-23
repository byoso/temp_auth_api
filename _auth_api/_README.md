# _auth_api

Complete authentication system ready for a SPA.

It will use a unique username and only one user can have the same email 'verified' at once.

_auth_api includes both endpoints and the classic views needed to interact with the auth system (mostly confirmation emails).

Only missing a social authentication...

## Installation

First, make a proper installation of django rest framework.

Use the `dependencies.txt` or manually pip install:

```sh
django
django-rest-framework
PyJWT
```

Then copy/paste the app `_auth_api` in your django's root directory.

**settings.py**
```python
INSTALLED_APPS = [
    '_auth_api',
]

# you must have a proper email configuration, for dev let's say just:
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Optionnaly (are given the default values):

_AUTH_API = {
    'URL_PREFIX': 'auth/',  # change the prefix of all the views and endpoints
    'SITE_NAME': None,  # str: used in email templates instead of host name if you want
    'EMAIL_VALID_TIME': 60 * 60 * 24 * 7,  # 7 days, JWT used in email links expiration time
}

```

**urls.py**
```python
urlpatterns = [
    # ...
    path('', include('_auth_api.urls'),)
    # only if you want to try the SPA demo:
    path('', TemplateView.as_view(template_name='_auth_api/demo.html')),
]
```

## Endpoints

Only 3 endpoints are absolutly necessary, check `_auth_api/urls.py` and uncomment the optionnal ones if you want (closed by default)

|uri | Method | form-data | Authorization | effect |
| --- | --- | --- | --- | --- |
| auth/api_signup/ | POST | username, email, password, password2 | - | Create a new user, send a confirmation email |
| auth/api_login/ | POST | credential, password | - | Log in, return a `auth_token` and a `user` |
| auth/api_logout/ | POST | - | Token [the auth_token] | log out, delete the auth token in the database |


## Views

Include this views in your project as simple links (GET).

| uri | effect |
| --- | --- |
| auth/password_reset_request/ | to ask for a password reset if the passowrd is forgotten. The user must have an already verified email account |
| auth/change_email/ | to ask for an email change |

The other views are the ones used following the links given in the emails.
