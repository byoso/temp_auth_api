from django.urls import path, include

from .config import _AUTH_API as conf
from . import views_api
from . import views


prefix = conf['URL_PREFIX']

urlpatterns = [
    # api views
    path(f'{prefix}api_signup/', views_api.Signup.as_view(), name="api_signup"),


    path(f'{prefix}token/login/', views_api.LoginWithAuthToken.as_view(), name="token_login"),  # normal login
    # path(f'{prefix}login_with_jwt/', views_api.LoginWithJWTToken.as_view(), name="login_with_jwt"),  # login from email
    path(f'{prefix}token/logout/', views_api.token_logout, name="token_logout"),
    path(
        f'{prefix}password/request_reset/',
        views_api.password_request_reset,
        name='password_request_reset'
    ),
    path(
        f'{prefix}email/confirm_email/resend/',
        views_api.email_confirm_email_resend,
        name="email_confirm_email_resend"
    ),
    path(
        f'{prefix}password/change/',
        views_api.password_change,
        name='password_change'
    ),
    path(
        f'{prefix}email/request_change/',
        views_api.email_request_change,
        name='email_request_change'
    ),
    path(
        f'{prefix}username/change/',
        views_api.username_change,
        name='username_change'
    ),
    path(f'{prefix}users/delete_me/', views_api.users_delete_me, name='users_delete_me'),
    path(f'{prefix}users/my_infos/', views_api.users_my_infos, name="users_my_infos"),

    # DO NOT not use this one in production:
    # path(f'{prefix}users/all/', views_api.get_users_all, name="get_users_all"),

    # classic views
    path(f'{prefix}confirm_email/<str:token>', views.ConfirmEmail.as_view(), name="confirm_email"),
]