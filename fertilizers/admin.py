from django.contrib import admin
from .models import Fertilizer, FertilizerRecommendation


@admin.register(FertilizerRecommendation)
class FertilizerRecommendationAdmin(admin.ModelAdmin):
    list_display = ('id', 'crop_name', 'fertilizer', 'district', 'growth_stage', 'total_quantity_farmer_land', 'created_at')
    list_filter = ('fertilizer', 'growth_stage', 'district')
    search_fields = ('crop_name', 'fertilizer__fertilizer_name', 'district')


@admin.register(Fertilizer)
class FertilizerAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'fertilizer_name', 'fertilizer_type',
        'nitrogen_percentage', 'phosphorus_percentage',
        'potassium_percentage', 'sulphur_percentage',
        'application_method', 'dosage_per_hectare'
    )
    list_filter = ('fertilizer_type',)
    search_fields = ('fertilizer_name', 'recommended_crops', 'description')
    ordering = ('fertilizer_name',)

    fieldsets = (
        ('General Details', {
            'fields': ('fertilizer_name', 'fertilizer_type', 'description')
        }),
        ('Nutrient Composition (%)', {
            'fields': (
                'nitrogen_percentage', 'phosphorus_percentage',
                'potassium_percentage', 'sulphur_percentage'
            )
        }),
        ('Application Recommendations', {
            'fields': (
                'recommended_crops', 'application_method',
                'dosage_per_hectare', 'application_timing', 'precautions'
            )
        }),
    )
