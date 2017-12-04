import random
import string

from django.contrib.auth.models import User
from django.db import models


class ApiUser(models.Model):
    def generate_token():
        return ''.join(
            random.SystemRandom().choice(
                string.ascii_letters + string.digits
            ) for _ in range(20))

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )
    token = models.SlugField(
        max_length=20,
        default=generate_token,
        editable=False,
        unique=True,
    )

    def __str__(self):
        return self.user.username
