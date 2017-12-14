from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
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
    name = serializers.CharField(validators=[])
    parent = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Domain.objects.all(),
        required=False,
        allow_null=True,
    )

    def create(self, validated_data):
        try:
            parent = Domain.objects.get(
                slug=validated_data.get('parent')
            )
        except ObjectDoesNotExist:
            parent = None
        domain, created = Domain.objects.get_or_create(
            name=validated_data.get('name'),
            defaults={"parent": parent}
        )
        return domain

    class Meta:
        model = Domain
        lookup_field = 'slug'
        fields = (
            'slug',
            'name',
            'parent',
        )


class EntityListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        entities = [Entity(**data) for data in validated_data]
        return Entity.objects.bulk_create(entities)


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
        allow_null=True,
        pk_field=serializers.UUIDField(format='hex_verbose'),
    )
    superseded_by = serializers.PrimaryKeyRelatedField(
        queryset=Entity.objects.all(),
        required=False,
        allow_null=True,
        pk_field=serializers.UUIDField(format='hex_verbose'),
    )

    class Meta:
        model = Entity
        list_serializer_class = EntityListSerializer
        fields = (
            'uuid',
            'attributes',
            'domain',
            'superseded_by',
            'alias_for',
        )
