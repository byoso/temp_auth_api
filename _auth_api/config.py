from django.conf import settings


_AUTH_API = {
    'URL_PREFIX': 'auth/',
    'SITE_NAME': None,
    'EMAIL_VALID_TIME': 60 * 60 * 24 * 7,  # 7 days,
}

_AUTH_API.update(getattr(settings, 'AUTH_API', {}))
