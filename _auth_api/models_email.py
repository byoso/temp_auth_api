from django.db import models
from django.contrib.auth import get_user_model

from .utils import (
    gettext_lazy as _,
)


User = get_user_model()


class EmailAddress(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        verbose_name=_("user"),
        on_delete=models.CASCADE,
        related_name="email_addresses",
    )
    email = models.EmailField(
        max_length=64,
        verbose_name=_("email address"),
    )
    verified = models.BooleanField(verbose_name=_("verified"), default=False)
    primary = models.BooleanField(verbose_name=_("primary"), default=False)

    def __str__(self):
        return self.email
