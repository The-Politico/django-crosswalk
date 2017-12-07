from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response

from crosswalk.authentication import AuthenticatedView
from crosswalk.exceptions import NestedAttributesError, ReservedKeyError
from crosswalk.models import Domain, Entity
from crosswalk.validators import (validate_no_reserved_keys,
                                  validate_shallow_dict)


class BulkCreate(AuthenticatedView):
    def post(self, request, domain):
        try:
            domain = Domain.objects.get(slug=domain)
        except ObjectDoesNotExist:
            Response({
                "message": "Domain not found."
            }, status=status.HTTP_200_OK)

        entities = request.data.copy()

        # Validate entity attributes before creating in bulk
        for entity in entities:
            try:
                validate_shallow_dict(entity)
            except NestedAttributesError:
                return Response({
                    "message": "Cannot create entity with nested attributes."
                }, status=status.HTTP_400_BAD_REQUEST)
            try:
                validate_no_reserved_keys(entity)
            except ReservedKeyError:
                return Response({
                    "message": "Reserved key found in entity attributes."
                }, status=status.HTTP_400_BAD_REQUEST)

        Entity.objects.bulk_create([
            Entity(domain=domain, attributes=entity)
            for entity in entities
        ])

        return Response({
            "message": "Created {} entities in bulk.".format(len(entities))
        }, status=status.HTTP_200_OK)
