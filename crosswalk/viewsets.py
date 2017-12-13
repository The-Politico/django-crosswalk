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
            data={"attributes": new_attributes},
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
