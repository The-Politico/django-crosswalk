from crosswalk.authentication import AuthenticatedView
from crosswalk.models import Domain, Entity
from crosswalk.serializers import EntitySerializer
from django.core.exceptions import ObjectDoesNotExist
from fuzzywuzzy import process
from rest_framework import status
from rest_framework.response import Response


class BestMatch(AuthenticatedView):
    def query(self):
        entities = Entity.objects.filter(domain=self.domain)
        entities = entities.filter(attributes__contains=self.block_attrs)

        entity_values = [e.attributes[self.query_field] for e in entities]
        match, score = process.extractOne(
            self.query_value,
            entity_values,
        )

        self.entity = entities.filter(
            **{'attributes__{}'.format(self.query_field): match}
        ).first()

        self.score = score

    def get(self, request, domain):
        """
        Get the best matched entity of a given query.

        If the entity is an alias or is superseded by another entity in another
        domain, the aliased or superseding entity is returned.
        """
        self.user = request.user
        params = request.query_params.copy()
        self.query_field = params.pop('query_field')[0]
        self.query_value = params.pop('query_value')[0]
        self.block_attrs = params

        try:
            self.domain = Domain.objects.get(slug=domain)
        except ObjectDoesNotExist:
            Response(
                "Domain not found.",
                status=status.HTTP_404_NOT_FOUND
            )

        self.query()

        aliased = False

        while self.entity.alias_for:
            aliased = True
            self.entity = self.entity.alias_for

        return Response({
            "entity": EntitySerializer(self.entity).data,
            "match_score": self.score,
            "aliased": aliased,
        }, status=status.HTTP_200_OK)

    def post(self, request, domain):
        """
        Create an entity if one is not found above a certain match threshold.

        If the found entity is an alias or is superseded by another entity in
        another domain, the aliased or superseding entity is returned.
        """
        self.user = request.user
        self.data = request.data.copy()
        self.query_field = self.data.get('query_field')
        self.query_value = self.data.get('query_value')
        self.block_attrs = self.data.get('block_attrs', {})
        self.create_attrs = self.data.get('create_attrs', {})
        threshold = self.data.get('create_threshold')

        try:
            self.domain = Domain.objects.get(slug=domain)
        except ObjectDoesNotExist:
            Response(
                "Domain not found.",
                status=status.HTTP_404_NOT_FOUND
            )

        self.query()

        created = False
        aliased = False

        if self.score < threshold:
            created = True
            uuid = self.create_attrs.pop('uuid', None)
            entity = Entity(
                uuid=uuid,
                attributes={
                    **{self.query_field: self.query_value},
                    **self.block_attrs,
                    **self.create_attrs,
                },
                created_by=self.user,
                domain=self.domain
            )
            entity.save()
            self.entity = entity

        while self.entity.alias_for:
            aliased = True
            self.entity = self.entity.alias_for

        return Response({
            "entity": EntitySerializer(self.entity).data,
            "created": created,
            "match_score": self.score,
            "aliased": aliased,
        }, status=status.HTTP_200_OK)
