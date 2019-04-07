from crosswalk.authentication import AuthenticatedView
from crosswalk.models import Domain, Entity
from crosswalk.serializers import EntitySerializer
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response


class MatchOrCreate(AuthenticatedView):
    def post(self, request, domain):
        """
        Get a matched entity for a given query or create an entity if
        one is not found.

        If the entity is an alias of another entity, the aliased entity is
        returned.
        """
        user = request.user
        data = request.data.copy()
        query_field = data.get("query_field")
        query_value = data.get("query_value")
        block_attrs = data.get("block_attrs", {})
        create_attrs = data.get("create_attrs", {})
        return_canonical = data.get("return_canonical", True)

        try:
            domain = Domain.objects.get(slug=domain)
        except ObjectDoesNotExist:
            return Response(
                "Domain not found.", status=status.HTTP_404_NOT_FOUND
            )

        entities = Entity.objects.filter(domain=domain)
        entities = entities.filter(attributes__contains=block_attrs)

        entities = entities.filter(
            **{"attributes__{}".format(query_field): query_value}
        )

        created = False
        aliased = False

        if entities.count() == 0:
            created = True
            uuid = create_attrs.pop("uuid", None)
            entity = Entity(
                uuid=uuid,
                attributes={
                    **{query_field: query_value},
                    **block_attrs,
                    **create_attrs,
                },
                created_by=user,
                domain=domain,
            )
            entity.save()
        elif entities.count() > 1:
            return Response(
                "Found more than one entity. Be more specific?",
                status=status.HTTP_403_FORBIDDEN,
            )
        else:
            entity = entities[0]

        if return_canonical:
            while entity.alias_for:
                aliased = True
                entity = entity.alias_for

        return Response(
            {
                "entity": EntitySerializer(entity).data,
                "created": created,
                "aliased": aliased,
            },
            status=status.HTTP_200_OK,
        )
