from django.conf import settings


QUICK_AUTH = {
    'DJANGO_MODE': 'CLASSIC',  # 'CLASSIC', 'API' or 'TEST'
    'BASE_TEMPLATE': 'auth/demo.html',
    'HOME_URL': '/',
    'URL_PREFIX': 'auth/',
    'SITE_NAME': None,
    'EMAIL_VALID_TIME': 60 * 60 * 24 * 7,  # 7 days,
}

QUICK_AUTH.update(getattr(settings, 'QUICK_AUTH', {}))
