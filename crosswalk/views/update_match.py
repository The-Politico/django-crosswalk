from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response

from crosswalk.authentication import AuthenticatedView
from crosswalk.exceptions import NestedAttributesError, ReservedKeyError
from crosswalk.models import Domain, Entity
from crosswalk.serializers import EntitySerializer
from crosswalk.validators import full_validation


class UpdateMatch(AuthenticatedView):
    def post(self, request, domain):
        """
        POST searches for an entity based on criteria. If only one entity is
        returned from query, it is updated. If more than one, return 403.
        """
        data = request.data.copy()

        try:
            domain = Domain.objects.get(slug=domain)
        except ObjectDoesNotExist:
            return Response(
                "Domain not found.", status=status.HTTP_404_NOT_FOUND
            )

        entities = Entity.objects.filter(domain=domain)
        entities = entities.filter(
            attributes__contains=data.get("block_attrs", {})
        )

        if entities.count() == 0:
            return Response(
                "Entity not found.", status=status.HTTP_404_NOT_FOUND
            )

        elif entities.count() > 1:
            return Response(
                "Found more than one entity. Be more specific?",
                status=status.HTTP_403_FORBIDDEN,
            )

        entity = entities.first()
        update_attrs = data.get("update_attrs", {})

        # validate data
        try:
            full_validation(update_attrs)
        except (NestedAttributesError, ReservedKeyError):
            return Response(
                "Update data could not be validated.",
                status=status.HTTP_400_BAD_REQUEST,
            )

        entity.attributes = {**entity.attributes, **update_attrs}
        entity.save()

        return Response(
            {"entity": EntitySerializer(entities.first()).data},
            status=status.HTTP_200_OK,
        )
