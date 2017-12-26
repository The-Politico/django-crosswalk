from crosswalk.authentication import AuthenticatedView
from crosswalk.models import Domain, Entity
from crosswalk.serializers import EntitySerializer
from crosswalk.utils import import_class
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response


class BestMatch(AuthenticatedView):
    def post(self, request, domain):
        """
        Get the best matched entity for a given query.

        If the entity is an alias of another entity, the aliased entity is
        returned.
        """
        data = request.data.copy()
        query_field = data.get('query_field')
        query_value = data.get('query_value')
        return_canonical = data.get('return_canonical', True)
        block_attrs = data.get('block_attrs', {})
        scorer_class = data.get('scorer', 'fuzzywuzzy.default_process')

        try:
            scorer = import_class('crosswalk.scorers.{}'.format(scorer_class))
        except ImportError:
            return Response(
                "Invalid scorer.",
                status=status.HTTP_400_BAD_REQUEST
            )

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

        if return_canonical:
            while entity.alias_for:
                aliased = True
                entity = entity.alias_for

        return Response({
            "entity": EntitySerializer(entity).data,
            "match_score": score,
            "aliased": aliased,
        }, status=status.HTTP_200_OK)
