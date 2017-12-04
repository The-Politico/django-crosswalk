from django.core.exceptions import ObjectDoesNotExist
from fuzzywuzzy import process
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .authentication import TokenAuthentication
from .models import Domain, Entity
from .serializers import EntitySerializer


class AuthenticatedView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


class ClientCheck(AuthenticatedView):
    def get(self, request):
        return Response(
            {'message': 'Client configured correctly'},
            status=status.HTTP_200_OK
        )


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
