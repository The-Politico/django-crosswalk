from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response

from crosswalk.authentication import AuthenticatedView
from crosswalk.models import Domain, Entity
from crosswalk.serializers import EntitySerializer
from crosswalk.utils import import_class


class BestMatch(AuthenticatedView):

    def get(self, request, domain):
        """
        Get the best matched entity of a given query.

        If the entity is an alias or is superseded by another entity in another
        domain, the aliased or superseding entity is returned.
        """
        params = request.query_params.copy()
        query_field = params.pop('query_field')[0]
        query_value = params.pop('query_value')[0]
        block_attrs = params
        scorer_class = params.get('scorer', 'fuzzywuzzy.default_process')
        scorer = import_class('crosswalk.scorers.{}'.format(scorer_class))

        try:
            domain = Domain.objects.get(slug=domain)
        except ObjectDoesNotExist:
            return Response(
                "Domain not found.",
                status=status.HTTP_404_NOT_FOUND
            )

        entities = Entity.objects.filter(domain=domain)
        entities = entities.filter(attributes__contains=block_attrs)

        entity_values = [e.attributes[query_field] for e in entities]
        match, score = scorer(query_value, entity_values)

        entity = entities.filter(
            **{'attributes__{}'.format(query_field): match}
        ).first()

        aliased = False

        while entity.alias_for:
            aliased = True
            entity = entity.alias_for

        return Response({
            "entity": EntitySerializer(entity).data,
            "match_score": score,
            "aliased": aliased,
        }, status=status.HTTP_200_OK)

    def post(self, request, domain):
        """
        Create an entity if one is not found above a certain match threshold.

        If the found entity is an alias or is superseded by another entity in
        another domain, the aliased or superseding entity is returned.
        """
        user = request.user
        data = request.data.copy()
        query_field = data.get('query_field')
        query_value = data.get('query_value')
        block_attrs = data.get('block_attrs', {})
        create_attrs = data.get('create_attrs', {})
        threshold = data.get('threshold')
        scorer_class = data.get('scorer', 'fuzzywuzzy.default_process')
        scorer = import_class('crosswalk.scorers.{}'.format(scorer_class))

        try:
            domain = Domain.objects.get(slug=domain)
        except ObjectDoesNotExist:
            return Response(
                "Domain not found.",
                status=status.HTTP_404_NOT_FOUND
            )

        entities = Entity.objects.filter(domain=domain)
        entities = entities.filter(attributes__contains=block_attrs)

        entity_values = [e.attributes[query_field] for e in entities]
        match, score = scorer(query_value, entity_values)

        entity = entities.filter(
            **{'attributes__{}'.format(query_field): match}
        ).first()

        created = False
        aliased = False

        if score < threshold:
            created = True
            uuid = create_attrs.pop('uuid', None)
            entity = Entity(
                uuid=uuid,
                attributes={
                    **{query_field: query_value},
                    **block_attrs,
                    **create_attrs,
                },
                created_by=user,
                domain=domain
            )
            entity.save()

        while entity.alias_for:
            aliased = True
            entity = entity.alias_for

        return Response({
            "entity": EntitySerializer(entity).data,
            "created": created,
            "match_score": score,
            "aliased": aliased,
        }, status=status.HTTP_200_OK)
