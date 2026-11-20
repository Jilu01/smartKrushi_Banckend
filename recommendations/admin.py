from django.contrib import admin
from .models import FarmerFarmProfile, CropRecommendation, PestDiseaseInformation


@admin.register(FarmerFarmProfile)
class FarmerFarmProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'farm_name', 'farmer', 'district', 'total_land_area', 'irrigation_type', 'soil_type')
    list_filter = ('district', 'irrigation_type', 'soil_type')
    search_fields = ('farm_name', 'district', 'taluka', 'village')


@admin.register(CropRecommendation)
class CropRecommendationAdmin(admin.ModelAdmin):
    list_display = ('id', 'district', 'season', 'land_area_ha', 'created_at')
    list_filter = ('district', 'season', 'created_at')
    search_fields = ('district', 'session_id')


@admin.register(PestDiseaseInformation)
class PestDiseaseInformationAdmin(admin.ModelAdmin):
    list_display = ('id', 'crop_name', 'pest_or_disease_name', 'category', 'risk_level')
    list_filter = ('category', 'risk_level')
    search_fields = ('crop_name', 'pest_or_disease_name')
