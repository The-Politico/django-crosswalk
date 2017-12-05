from django.core.exceptions import ObjectDoesNotExist
from fuzzywuzzy import process
from rest_framework import status
from rest_framework.response import Response

from crosswalk.authentication import AuthenticatedView
from crosswalk.models import Domain, Entity
from crosswalk.serializers import EntitySerializer


class BestMatch(AuthenticatedView):
    def query(self, domain_slug):
        try:
            self.domain = Domain.objects.get(slug=domain_slug)
        except ObjectDoesNotExist:
            Response(
                {"message": "Domain not found."},
                status=status.HTTP_200_OK
            )

        entities = Entity.objects.filter(domain=self.domain)
        entities = entities.filter(attributes__contains=self.match_attrs)

        entity_values = [e.attributes[self.query_field] for e in entities]
        match, score = process.extractOne(self.query_value, entity_values)

        self.entity = entities.filter(
            **{'attributes__{}'.format(self.query_field): match}
        ).first()

        self.score = score

    def get(self, request, domain):
        """
        GET uses fuzzywuzzy to return the best match for a query.
        """
        self.user = request.user
        params = request.query_params.copy()
        self.query_field = params.pop('query_field')[0]
        self.query_value = params.pop('query_value')[0]
        self.match_attrs = params
        self.query(domain)

        return Response(
            {
                "entity": EntitySerializer(self.entity).data,
                "match_score": self.score,
            },
            status=status.HTTP_200_OK
        )

    def post(self, request, domain):
        """
        POST allows for creating an entity if one is not found above a certain
        match threshold, provided by fuzzywuzzy.
        """
        self.user = request.user
        self.data = request.data.copy()
        self.query_field = self.data.get('query_field')
        self.query_value = self.data.get('query_value')
        self.match_attrs = self.data.get('match_attrs', {})
        threshold = self.data.get('create_threshold')
        self.query(domain)

        created = False
        if self.score < threshold:
            created = True
            entity = Entity(
                attributes={
                    **{self.query_field: self.query_value},
                    **self.match_attrs,
                },
                created_by=self.user,
                domain=self.domain
            )
            entity.save()
            self.entity = entity

        return Response(
            {
                "entity": EntitySerializer(self.entity).data,
                "created": created,
                "match_score": self.score,
            },
            status=status.HTTP_200_OK
        )
