import uuid

from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db import models
from uuslug import uuslug


class Domain(models.Model):
    slug = models.SlugField(
        blank=True, max_length=250, unique=True, editable=False)

    name = models.CharField(max_length=250, unique=True)

    parent = models.ForeignKey(
        'self', null=True, blank=True, related_name='children')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuslug(
                self.name,
                instance=self,
                max_length=250,
                separator='-',
                start_no=2
            )
        super(Domain, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Entity(models.Model):
    uuid = models.UUIDField(
        default=uuid.uuid4, editable=False, primary_key=True)

    domain = models.ForeignKey(Domain, related_name='entities')

    attributes = JSONField()

    alias_for = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='aliases',
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
        help_text=(
            "An entity in another domain whose UUID should supersede",
            "this one."
        ),
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, related_name="+")

    @property
    def is_alias(self):
        return bool(self.alias_for)

    @property
    def is_superseded(self):
        return bool(self.superseded_by)

    def __str__(self):
        return self.uuid
