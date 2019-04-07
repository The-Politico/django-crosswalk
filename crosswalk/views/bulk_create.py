from crosswalk.authentication import AuthenticatedView
from crosswalk.exceptions import NestedAttributesError, ReservedKeyError
from crosswalk.models import Domain, Entity
from crosswalk.serializers import EntitySerializer
from crosswalk.validators import (
    validate_no_reserved_keys,
    validate_shallow_dict,
)
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response


class BulkCreate(AuthenticatedView):
    def post(self, request, domain):
        try:
            domain = Domain.objects.get(slug=domain)
        except ObjectDoesNotExist:
            return Response("Domain not found.", status=status.HTTP_200_OK)

        entities = request.data.copy()

        entity_objects = []

        for entity in entities:
            uuid = entity.pop("uuid", None)

            # Validate entity attributes before creating in bulk
            try:
                validate_shallow_dict(entity)
            except NestedAttributesError:
                return Response(
                    "Cannot create entity with nested attributes.",
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                validate_no_reserved_keys(entity)
            except ReservedKeyError:
                return Response(
                    "Reserved key found in entity attributes.",
                    status=status.HTTP_400_BAD_REQUEST,
                )

            entity_objects.append(
                Entity(
                    uuid=uuid,
                    domain=domain,
                    attributes=entity,
                    created_by=request.user,
                )
            )

        created_entities = Entity.objects.bulk_create(entity_objects)

        return Response(
            {
                "entities": [
                    {"entity": EntitySerializer(entity).data, "created": True}
                    for entity in created_entities
                ]
            },
            status=status.HTTP_200_OK,
        )
