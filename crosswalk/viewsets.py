from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from crosswalk.authentication import TokenAuthentication

from .models import Domain, Entity
from .serializers import DomainSerializer, EntitySerializer


class AuthenticatedViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    paginator = None


class DomainViewSet(AuthenticatedViewSet):
    serializer_class = DomainSerializer
    lookup_field = "slug"

    def get_queryset(self):
        queryset = Domain.objects.all()
        parent = self.request.query_params.get("parent", None)
        if parent:
            queryset = queryset.filter(parent__slug=parent)
        return queryset


class EntityDomainViewSet(AuthenticatedViewSet):
    serializer_class = EntitySerializer

    def get_queryset(self):
        domain = self.kwargs["domain"]
        return Entity.objects.filter(domain__name=domain)

    def list(self, request, domain):
        """Allow passing block attr params to filter queryset."""
        params = request.query_params.copy()
        queryset = self.get_queryset().filter(attributes__contains=params)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class EntityViewSet(AuthenticatedViewSet):
    serializer_class = EntitySerializer
    queryset = Entity.objects.all()

    def partial_update(self, request, pk=None):
        """
        Merge attributes dict with existing attributes.
        """
        instance = self.queryset.get(pk=pk)
        new_attributes = {
            **instance.attributes,
            **request.data.get("attributes", {}),
        }
        serializer = self.serializer_class(
            instance,
            data={
                "attributes": new_attributes,
                "alias_for": request.data.get("alias_for", instance.alias_for),
                "superseded_by": request.data.get(
                    "superseded_by", instance.superseded_by
                ),
            },
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
