from crosswalk.authentication import AuthenticatedView
from crosswalk.models import Domain, Entity
from crosswalk.serializers import EntitySerializer
from django.core.exceptions import ObjectDoesNotExist
from fuzzywuzzy import process
from rest_framework import status
from rest_framework.response import Response


class BestMatch(AuthenticatedView):
    def domain_set(self):
        self.entities = Entity.objects.filter(domain=self.domain)

    def match_set(self, match_attrs):
        self.entities = self.entities.filter(attributes__contains=match_attrs)

    def subset(self, domain_slug):
        try:
            domain = Domain.objects.get(slug=domain_slug)
        except ObjectDoesNotExist:
            Response(
                {"message": "Domain not found."},
                status=status.HTTP_200_OK
            )
        self.domain = domain
        self.domain_set()
        match_attrs = self.data.get('match_attrs', None)
        if match_attrs:
            self.match_set(match_attrs)

    def query(self, request, query):
        field = query['field']
        value = query['value']
        entities = [e.attributes[field] for e in self.entites]
        match, score = process.extractOne(value, entities)
        entity = self.entities.filter(
            **{'attributes__{}'.format(field): match}
        )[0]

    def post(self, request, domain):
        self.user = request.user
        self.data = request.data
        self.subset(request, domain)
        serializer = EntitySerializer(self.entities, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
