from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response

from crosswalk.authentication import AuthenticatedView
from crosswalk.models import Domain, Entity


class BulkCreate(AuthenticatedView):
    def post(self, request, domain):
        try:
            domain = Domain.objects.get(slug=domain)
        except ObjectDoesNotExist:
            Response(
                {"message": "Domain not found."},
                status=status.HTTP_200_OK
            )
        entities = request.data.get('entities', [])
        if request.data.get('force_bulk', False):
            Entity.objects.bulk_create([
                Entity(domain=domain, attributes=entity)
                for entity in entities
            ])
        else:
            for entity in entities:
                Entity.objects.get_or_create(
                    domain=domain,
                    attributes=entity
                )
        Response(
            {"message": "Created {} entities.".format(len(entities))},
            status=status.HTTP_200_OK
        )
