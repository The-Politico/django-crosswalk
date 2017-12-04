from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Domain, Entity


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
        )


class DomainSerializer(serializers.ModelSerializer):
    parent = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Domain.objects.all(),
        required=False,
    )

    class Meta:
        model = Domain
        lookup_field = 'slug'
        fields = (
            'slug',
            'name',
            'parent',
        )


class EntitySerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(
        format='hex_verbose',
        required=False,
    )
    domain = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Domain.objects.all(),
    )
    alias_for = serializers.PrimaryKeyRelatedField(
        queryset=Entity.objects.all(),
        required=False,
        pk_field=serializers.UUIDField(format='hex_verbose'),
    )
    superseded_by = serializers.PrimaryKeyRelatedField(
        queryset=Entity.objects.all(),
        required=False,
        pk_field=serializers.UUIDField(format='hex_verbose'),
    )

    class Meta:
        model = Entity
        fields = (
            'uuid',
            'attributes',
            'domain',
            'created',
            'updated',
            'superseded_by',
            'alias_for',
            'created_by',
        )
