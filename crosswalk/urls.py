from django.urls import include, path
from rest_framework import routers

from .views import (
    AliasOrCreate,
    BestMatch,
    BestMatchOrCreate,
    BulkCreate,
    ClientCheck,
    DeleteMatch,
    MatchOrCreate,
    Match,
    UpdateMatch,
)
from .viewsets import DomainViewSet, EntityDomainViewSet, EntityViewSet

router = routers.DefaultRouter()

router.register("domains", DomainViewSet, basename="domains")

entity_detail = EntityViewSet.as_view(
    {
        "get": "retrieve",
        "put": "update",
        "patch": "partial_update",
        "delete": "destroy",
    }
)
entity_domain_list = EntityDomainViewSet.as_view(
    {"get": "list", "post": "create"}
)
entity_domain_detail = EntityDomainViewSet.as_view(
    {
        "get": "retrieve",
        "put": "update",
        "patch": "partial_update",
        "delete": "destroy",
    }
)

urlpatterns = [
    path("api/", include(router.urls)),
    path(
        "api/domains/<slug:domain>/entities/",
        entity_domain_list,
        name="crosswalk-entity-domain-lists",
    ),
    path(
        "api/domains/<slug:domain>/entities/bulk-create/", BulkCreate.as_view()
    ),
    path(
        "api/domains/<slug:domain>/entities/best-match/", BestMatch.as_view()
    ),
    path(
        "api/domains/<slug:domain>/entities/best-match-or-create/",
        BestMatchOrCreate.as_view(),
    ),
    path("api/domains/<slug:domain>/entities/match/", Match.as_view()),
    path(
        "api/domains/<slug:domain>/entities/match-or-create/",
        MatchOrCreate.as_view(),
    ),
    path(
        "api/domains/<slug:domain>/entities/delete-match/",
        DeleteMatch.as_view(),
    ),
    path(
        "api/domains/<slug:domain>/entities/update-match/",
        UpdateMatch.as_view(),
    ),
    path(
        "api/domains/<slug:domain>/entities/alias-or-create/",
        AliasOrCreate.as_view(),
    ),
    path(
        "api/domains/<slug:domain>/entities/<uuid:pk>/",
        entity_domain_detail,
        name="crosswalk-entity-domain-detail",
    ),
    path(
        "api/entities/<uuid:pk>/",
        entity_detail,
        name="crosswalk-entity-detail",
    ),
    path("api/client-check/", ClientCheck.as_view()),
]
