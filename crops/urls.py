from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CropViewSet,
    CropRecordViewSet,
    CropSeasonCalendarViewSet,
    CropProductionHistoryViewSet,
    CropCostViewSet,
    CropMarketPriceViewSet,
    CropCategoryViewSet,
    CropLocationSuitabilityViewSet
)

router = DefaultRouter()
router.register('categories', CropCategoryViewSet, basename='crop-categories')
router.register('suitability', CropLocationSuitabilityViewSet, basename='crop-location-suitability')
router.register('season-calendar', CropSeasonCalendarViewSet, basename='crop-season-calendar')
router.register('production-history', CropProductionHistoryViewSet, basename='crop-production-history')
router.register('costs', CropCostViewSet, basename='crop-costs')
router.register('market-prices', CropMarketPriceViewSet, basename='crop-market-prices')
router.register('records', CropRecordViewSet, basename='crop-records')
router.register('', CropViewSet, basename='crops')

urlpatterns = [
    path('', include(router.urls)),
]
