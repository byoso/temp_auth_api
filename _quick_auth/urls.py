from django.urls import path, include
from django.contrib.auth.views import LogoutView

from .config import QUICK_AUTH as conf
from . import views, views_classic

if conf['DJANGO_MODE'] == 'API':
    from . import views_api

prefix = conf['URL_PREFIX']

urlpatterns = [
    # classic views for confirmations and password reset, used both with API and CLASSIC modes
    path(f'{prefix}confirm_email/<str:token>', views.ConfirmEmail.as_view(), name="confirm_email"),
    path(
        f'{prefix}change_email/',
        views.ChangeEmailView.as_view(),
        name="change_email"
    ),
    path(
        f'{prefix}password_reset_request/',
        views.PasswordResetRequest.as_view(),
        name='password_reset_request'
    ),
    path(
        f'{prefix}password_reset/<str:token>',
        views.PasswordReset.as_view(),
        name='password_reset'
    ),]

classic_urlpatterns = [
    path('accounts/login/', views_classic.Login.as_view(), name="login"),
    path('accounts/logout/', views_classic.Logout.as_view(), name="logout"),
    path('accounts/signup/', views_classic.Signup.as_view(), name="signup"),
]

#  Conditionnal is to avoid errors if DRF is not installed
if conf['DJANGO_MODE'] == 'API':
    api_urlpatterns = [
        # api main endpoints
        path(f'{prefix}api_signup/', views_api.Signup.as_view(), name="api_signup"),
        path(f'{prefix}api_login/', views_api.LoginWithAuthToken.as_view(), name="api_login"),
        path(f'{prefix}api_logout/', views_api.token_logout, name="token_logout"),

        # api optionnal endpoints
        # path(
        #     f'{prefix}username/change/',
        #     views_api.username_change,
        #     name='username_change'
        # ),
        # path(f'{prefix}delete_me/', views_api.users_delete_me, name='users_delete_me'),
        # path(f'{prefix}my_infos/', views_api.users_my_infos, name="users_my_infos"),

        # do NOT not use this one in production:
        # path(f'{prefix}users/all/', views_api.get_users_all, name="get_users_all"),
    ]
else:
    api_urlpatterns = []


if conf['DJANGO_MODE'] in ['CLASSIC', 'TEST']:
    urlpatterns += classic_urlpatterns

if conf['DJANGO_MODE'] in ['API', 'TEST']:
    urlpatterns += api_urlpatterns
