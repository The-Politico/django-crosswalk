from crosswalk.authentication import TokenAuthentication
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Domain, Entity
from .serializers import DomainSerializer, EntitySerializer


class DomainViewSet(viewsets.ModelViewSet):
    serializer_class = DomainSerializer
    queryset = Domain.objects.all()
    lookup_field = 'slug'


class EntityDomainViewSet(viewsets.ModelViewSet):
    serializer_class = EntitySerializer

    def get_queryset(self):
        domain = self.kwargs['domain']
        return Entity.objects.filter(domain__name=domain)

    def list(self, request, domain):
        """Allow passing block attr params to filter queryset."""
        params = request.query_params.copy()
        queryset = self.get_queryset().filter(attributes__contains=params)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class EntityViewSet(viewsets.ModelViewSet):
    serializer_class = EntitySerializer
    queryset = Entity.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def partial_update(self, request, pk=None):
        """
        Merge attributes dict with existing attributes.
        """
        instance = self.queryset.get(pk=pk)
        new_attributes = {
            **instance.attributes,
            **request.data.get('attributes', {})
        }
        serializer = self.serializer_class(
            instance,
            data={
                "attributes": new_attributes,
                "alias_for": request.data.get(
                    "alias_for",
                    instance.alias_for
                ),
                "superseded_by": request.data.get(
                    "superseded_by",
                    instance.superseded_by
                )
            },
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
