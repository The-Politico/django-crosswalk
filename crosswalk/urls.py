from django.urls import include, path
from rest_framework import routers

from .views import BestMatch, BulkCreate, ClientCheck
from .viewsets import DomainViewSet, EntityViewSet

router = routers.DefaultRouter()

router.register(r'entities', EntityViewSet, base_name='crosswalk_entities')
router.register(r'domains', DomainViewSet)

urlpatterns = [
    path(r'api/', include(router.urls)),
    path(r'api/bulk-create/<slug:domain>/', BulkCreate.as_view()),
    path(r'api/best-match/<slug:domain>/', BestMatch.as_view()),
    path(r'api/client-check/', ClientCheck.as_view())
]
