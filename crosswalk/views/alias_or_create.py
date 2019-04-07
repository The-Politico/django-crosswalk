from crosswalk.authentication import AuthenticatedView
from crosswalk.models import Domain, Entity
from crosswalk.serializers import EntitySerializer
from crosswalk.utils import import_class
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response


class AliasOrCreate(AuthenticatedView):
    def post(self, request, domain):
        """
        Create an alias if an entity is found above a certain match threshold
        or create a new entity.
        """
        user = request.user
        data = request.data.copy()
        query_field = data.get("query_field")
        query_value = data.get("query_value")
        block_attrs = data.get("block_attrs", {})
        create_attrs = data.get("create_attrs", {})
        return_canonical = data.get("return_canonical", True)
        threshold = data.get("threshold")
        scorer_class = data.get("scorer", "fuzzywuzzy.default_process")

        try:
            scorer = import_class("crosswalk.scorers.{}".format(scorer_class))
        except ImportError:
            return Response(
                "Invalid scorer.", status=status.HTTP_400_BAD_REQUEST
            )

        try:
            domain = Domain.objects.get(slug=domain)
        except ObjectDoesNotExist:
            return Response(
                "Domain not found.", status=status.HTTP_404_NOT_FOUND
            )

        # Find the best match for a query
        entities = Entity.objects.filter(domain=domain)
        entities = entities.filter(attributes__contains=block_attrs)

        entity_values = [e.attributes[query_field] for e in entities]
        match, score = scorer(query_value, entity_values)

        entities = entities.filter(
            **{"attributes__{}".format(query_field): match}
        )

        if entities.count() > 1:
            return Response(
                "More than one alias candiate for entity.",
                status=status.HTTP_403_FORBIDDEN,
            )

        entity = entities.first()

        attributes = {
            **{query_field: query_value},
            **block_attrs,
            **create_attrs,
        }

        if entity.attributes == attributes:
            return Response(
                "Entity appears to already exist.",
                status=status.HTTP_409_CONFLICT,
            )

        if score > threshold:
            aliased = True
            alias = Entity(
                attributes=attributes,
                alias_for=entity,
                created_by=user,
                domain=domain,
            )
            alias.save()
            if return_canonical:
                while entity.alias_for:
                    entity = entity.alias_for
        else:
            aliased = False
            entity = Entity(
                attributes=attributes, created_by=user, domain=domain
            )
            entity.save()

        return Response(
            {
                "entity": EntitySerializer(entity).data,
                "created": True,
                "aliased": aliased,
                "match_score": score,
            },
            status=status.HTTP_200_OK,
        )
