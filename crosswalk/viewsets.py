import django_filters.rest_framework
from rest_framework import viewsets

from .models import Domain, Entity
from .serializers import DomainSerializer, EntitySerializer


class DomainViewSet(viewsets.ModelViewSet):
    serializer_class = DomainSerializer
    queryset = Domain.objects.all()
    lookup_field = 'slug'


class EntityViewSet(viewsets.ModelViewSet):
    serializer_class = EntitySerializer

    def get_queryset(self):
        domain = self.kwargs['domain']
        return Entity.objects.filter(domain__name=domain)
