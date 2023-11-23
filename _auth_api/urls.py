from django.urls import path, include

from .config import _AUTH_API as conf
from . import views_api
from . import views


prefix = conf['URL_PREFIX']

urlpatterns = [
    # api main endpoints
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

    # do NOT not use this one in production:
    # path(f'{prefix}users/all/', views_api.get_users_all, name="get_users_all"),

    # classic views
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
    ),
]
