from crosswalk.authentication import AuthenticatedView
from crosswalk.models import Domain, Entity
from crosswalk.serializers import EntitySerializer
from django.core.exceptions import ObjectDoesNotExist
from fuzzywuzzy import process
from rest_framework import status
from rest_framework.response import Response


class CreateMatchedAlias(AuthenticatedView):

    def post(self, request, domain):
        """
        Create an alias if an entity is found above a certain match threshold.
        """
        user = request.user
        data = request.data.copy()
        query_field = data.get('query_field')
        query_value = data.get('query_value')
        match_attrs = data.get('match_attrs', {})
        create_attrs = data.get('create_attrs', {})
        threshold = data.get('create_threshold')

        try:
            domain = Domain.objects.get(slug=domain)
        except ObjectDoesNotExist:
            Response({
                "message": "Domain not found."
            }, status=status.HTTP_404_NOT_FOUND)

        entities = Entity.objects.filter(domain=domain)
        entities = entities.filter(attributes__contains=match_attrs)

        entity_values = [e.attributes[query_field] for e in entities]
        match, score = process.extractOne(
            query_value,
            entity_values,
        )

        entity = entities.filter(
            **{'attributes__{}'.format(query_field): match}
        ).first()

        entities = Entity.objects.filter(domain=domain)
        entities = entities.filter(attributes__contains=match_attrs)

        entity_values = [e.attributes[query_field] for e in entities]
        match, score = process.extractOne(
            query_value,
            entity_values,
        )

        entities = entities.filter(
            **{'attributes__{}'.format(query_field): match}
        )

        if entities.count() > 1:
            return Response({
                "message": (
                    "Found more than one alias candiate for entity. "
                    "Be more specific?"
                )
            }, status=status.HTTP_403_FORBIDDEN)

        entity = entities.first()

        created = False
        aliased = False
        superseding = False

        while entity.alias_for:
            aliased = True
            entity = entity.alias_for

        while entity.superseded_by:
            superseding = True
            entity = entity.superseded_by

        if score > threshold:
            created = True
            aliased = True
            alias = Entity(
                attributes={
                    **{query_field: query_value},
                    **match_attrs,
                    **create_attrs
                },
                alias_for=entity,
                created_by=user,
                domain=domain
            )
            alias.save()

            return Response({
                "entity": EntitySerializer(entity).data,
                "created": created,
                "aliased": aliased,
                "superseding": superseding,
                "match_score": score,
            }, status=status.HTTP_200_OK)

        return Response({
            "message": "No alias candidate found above threshold."
        }, status=status.HTTP_404_NOT_FOUND)
