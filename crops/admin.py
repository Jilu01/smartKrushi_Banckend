from django.contrib import admin
from .models import (
    CropData, Crop, CropRecord,
    CropCategory, CropLocationSuitability,
    CropSeasonCalendar, CropProductionHistory,
    CropCost, CropMarketPrice
)


@admin.register(CropCategory)
class CropCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'category_code', 'category_name', 'category_name_gujarati', 'display_order')
    search_fields = ('category_name', 'category_name_gujarati', 'category_code')
    ordering = ('display_order', 'category_name')


@admin.register(CropSeasonCalendar)
class CropSeasonCalendarAdmin(admin.ModelAdmin):
    list_display = ('id', 'crop', 'district', 'season', 'sowing_start_month', 'sowing_end_month', 'harvest_start_month', 'harvest_end_month')
    list_filter = ('season', 'district', 'state')
    search_fields = ('crop__crop_name', 'district')


@admin.register(CropLocationSuitability)
class CropLocationSuitabilityAdmin(admin.ModelAdmin):
    list_display = ('id', 'crop', 'district', 'taluka', 'suitability_level', 'suitability_score')
    list_filter = ('suitability_level', 'district')
    search_fields = ('crop__crop_name', 'district', 'taluka')


@admin.register(CropProductionHistory)
class CropProductionHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'crop_name', 'district', 'year', 'season', 'cultivated_area_hectares', 'production_tonnes', 'yield_kg_per_hectare')
    list_filter = ('year', 'season', 'district')
    search_fields = ('crop_name', 'district')


@admin.register(CropCost)
class CropCostAdmin(admin.ModelAdmin):
    list_display = ('id', 'crop', 'district', 'year', 'cost_unit', 'total_cultivation_cost')
    list_filter = ('year', 'cost_unit', 'district')
    search_fields = ('crop__crop_name', 'district')


@admin.register(CropMarketPrice)
class CropMarketPriceAdmin(admin.ModelAdmin):
    list_display = ('id', 'crop_name', 'district', 'apmc_market', 'date', 'modal_price', 'price_unit', 'price_trend')
    list_filter = ('date', 'price_trend', 'district')
    search_fields = ('crop_name', 'apmc_market', 'district')


@admin.register(CropData)
class CropDataAdmin(admin.ModelAdmin):
    list_display = (
        'crop_record_id',
        'state',
        'district',
        'crop_name',
        'growing_season',
        'crop_duration_days',
        'illustrative_yield_kg_ha',
    )
    search_fields = ('state', 'district', 'crop_name')
    list_filter = ('state', 'district', 'growing_season')
    ordering = ('state', 'district', 'crop_name')


@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'crop_name', 'scientific_name', 'crop_category',
        'growing_season', 'crop_duration_days', 'suitable_soil',
        'suitable_ph_min', 'suitable_ph_max', 'water_requirement'
    )
    list_filter = ('crop_category', 'growing_season', 'water_requirement')
    search_fields = ('crop_name', 'scientific_name', 'suitable_soil', 'crop_description')
    ordering = ('crop_name',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('crop_name', 'scientific_name', 'crop_category', 'crop_description', 'image')
        }),
        ('Growing Requirements', {
            'fields': (
                'growing_season', 'crop_duration_days', 'suitable_soil',
                'suitable_ph_min', 'suitable_ph_max', 'temperature_min', 'temperature_max',
                'water_requirement', 'rainfall_requirement', 'fertilizer_requirement'
            )
        }),
        ('Agronomic Practice', {
            'fields': ('sowing_period', 'harvesting_period', 'irrigation_method', 'common_diseases')
        }),
    )


@admin.register(CropRecord)
class CropRecordAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'state', 'district', 'taluka', 'crop_name',
        'growing_season', 'area_hectares', 'production_tonnes',
        'yield_kg_per_hectare', 'year', 'data_source'
    )
    list_filter = ('year', 'growing_season', 'state', 'district')
    search_fields = ('state', 'district', 'taluka', 'crop_name')
    ordering = ('-year', 'state', 'district', 'crop_name')