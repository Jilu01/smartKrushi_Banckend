from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StateViewSet, DistrictViewSet, TalukaViewSet, VillageViewSet,
    LocationDetectView, LocationHierarchyView, LocationBulkImportView
)

router = DefaultRouter()
router.register('states', StateViewSet, basename='location-states')
router.register('districts', DistrictViewSet, basename='location-districts')
router.register('talukas', TalukaViewSet, basename='location-talukas')
router.register('villages', VillageViewSet, basename='location-villages')

urlpatterns = [
    path('detect/', LocationDetectView.as_view(), name='location-detect'),
    path('hierarchy/', LocationHierarchyView.as_view(), name='location-hierarchy'),
    path('bulk-import/', LocationBulkImportView.as_view(), name='location-bulk-import'),
    path('', include(router.urls)),
]
