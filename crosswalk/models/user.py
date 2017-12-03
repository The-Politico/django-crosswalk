import uuid

from django.contrib.auth.models import User
from django.db import models


class ApiUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.UUIDField(
        default=uuid.uuid4, editable=False, primary_key=True)

    def __str__(self):
        return '{} {}'.format(
            self.user.first_name,
            self.user.last_name
        )
