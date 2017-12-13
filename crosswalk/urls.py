from django.urls import include, path
from rest_framework import routers

from .views import (BestMatch, BulkCreate, ClientCheck, CreateMatchedAlias,
                    DeleteMatch)
from .viewsets import DomainViewSet, EntityViewSet

router = routers.DefaultRouter()

router.register('domains', DomainViewSet)

entity_list = EntityViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
entity_detail = EntityViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = [
    path('api/', include(router.urls)),
    path(
        'api/entities/<slug:domain>/', entity_list,
        name="crosswalk-entity-lists"
    ),
    path(
        'api/entities/<slug:domain>/<uuid:pk>/', entity_detail,
        name="crosswalk-entity-detail"
    ),
    path('api/bulk-create/<slug:domain>/', BulkCreate.as_view()),
    path('api/best-match/<slug:domain>/', BestMatch.as_view()),
    path('api/delete-match/<slug:domain>/', DeleteMatch.as_view()),
    path(
        'api/create-matched-alias/<slug:domain>/',
        CreateMatchedAlias.as_view()
    ),
    path('api/client-check/', ClientCheck.as_view()),
]
