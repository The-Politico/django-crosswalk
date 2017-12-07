import uuid

from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db import models

from crosswalk.models import Domain
from crosswalk.validators import validate_shallow_dict


class Entity(models.Model):
    uuid = models.UUIDField(
        default=uuid.uuid4, editable=False, primary_key=True)

    domain = models.ForeignKey(
        Domain,
        related_name='entities',
        on_delete=models.PROTECT,
    )

    attributes = JSONField(validators=[validate_shallow_dict])

    alias_for = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='aliases',
        on_delete=models.PROTECT,
        help_text=(
            "An entity in the same domain whose UUID should supersede",
            "this one."
        ),
    )

    superseded_by = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='supersedes',
        on_delete=models.PROTECT,
        help_text=(
            "An entity in another domain whose UUID should supersede",
            "this one."
        ),
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        related_name="+",
        null=True,
        on_delete=models.SET_NULL
    )

    @property
    def is_alias(self):
        return bool(self.alias_for)

    @property
    def is_superseded(self):
        return bool(self.superseded_by)

    def __str__(self):
        return self.attributes.get('name', self.uuid.hex)
