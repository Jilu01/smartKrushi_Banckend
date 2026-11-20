from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class FarmerFarmProfile(models.Model):
    IRRIGATION_CHOICES = [
        ('Drip', 'Drip Irrigation (ટપક પદ્ધતિ)'),
        ('Sprinkler', 'Sprinkler Irrigation (ફુવારા પદ્ધતિ)'),
        ('Canal', 'Canal Flood Irrigation (નહેર સિંચાઈ)'),
        ('Borewell', 'Borewell / Tube well (બોરવેલ / કૂવો)'),
        ('Rainfed', 'Purely Rainfed / Dryland (વરસાદ આધારિત)'),
    ]

    farmer = models.ForeignKey(
        'accounts.FarmerProfile',
        on_delete=models.CASCADE,
        related_name='farm_profiles',
        null=True,
        blank=True
    )
    farm_name = models.CharField(max_length=150, default='My Farm / ખેતર')
    state = models.CharField(max_length=100, default='Gujarat', db_index=True)
    district = models.CharField(max_length=100, db_index=True)
    taluka = models.CharField(max_length=100, blank=True, null=True)
    village = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    total_land_area = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0.05)],
        help_text="Total cultivated area in hectares"
    )
    irrigation_type = models.CharField(
        max_length=100,
        choices=IRRIGATION_CHOICES,
        default='Borewell'
    )
    soil_type = models.CharField(max_length=100, default='Black')

    # Optional laboratory field test results
    has_soil_test = models.BooleanField(default=False)
    soil_ph = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(14.0)]
    )
    nitrogen = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0.0)])
    phosphorus = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0.0)])
    potassium = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0.0)])
    organic_carbon = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0.0)])
    soil_moisture = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0.0)])

    budget = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0)],
        help_text="Available working capital / budget in ₹"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'farmer_farm_profiles'
        ordering = ['-created_at']

    def __str__(self):
        loc = f"{self.village or self.taluka or self.district}, {self.district}"
        return f"{self.farm_name} ({self.total_land_area} ha) - {loc}"

    @property
    def land_area_acres(self):
        return round(self.total_land_area * 2.47105, 2)


class CropRecommendation(models.Model):
    farm_profile = models.ForeignKey(
        FarmerFarmProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recommendation_sessions'
    )
    farmer = models.ForeignKey(
        'accounts.FarmerProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='crop_recommendations'
    )
    session_id = models.CharField(max_length=64, db_index=True)

    # Location criteria
    state = models.CharField(max_length=100, default='Gujarat')
    district = models.CharField(max_length=100, db_index=True)
    taluka = models.CharField(max_length=100, blank=True, null=True)
    village = models.CharField(max_length=100, blank=True, null=True)
    season = models.CharField(max_length=50, default='Kharif', db_index=True)
    land_area_ha = models.FloatField(default=1.0)

    # Results & environmental telemetry snapshot
    top_recommended_crops = models.JSONField(default=list, help_text="Ranked top 5 crops with scores, yield, revenue, net profit")
    weather_summary = models.JSONField(default=dict)
    soil_summary = models.JSONField(default=dict)
    data_provenance = models.JSONField(default=dict, help_text="Actual/Estimated/Predicted labels and data source origins")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'crop_recommendation_history'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['district', 'season', 'created_at']),
            models.Index(fields=['session_id']),
        ]

    def __str__(self):
        return f"Recommendation #{self.id} for {self.district} ({self.season}) @ {self.created_at.strftime('%Y-%m-%d')}"


# Architecture Master Alias
RecommendationHistory = CropRecommendation


class PestDiseaseInformation(models.Model):
    CATEGORY_CHOICES = [
        ('Fungal', 'Fungal Disease'),
        ('Bacterial', 'Bacterial Disease'),
        ('Viral', 'Viral Disease'),
        ('Pest', 'Insect / Pest Infestation'),
        ('Physiological', 'Physiological Disorder'),
    ]

    RISK_CHOICES = [
        ('Low', 'Low Risk (સામાન્ય)'),
        ('Medium', 'Moderate Risk (મધ્યમ જોખમ)'),
        ('High', 'High Epidemic Risk (ઉચ્ચ જોખમ)'),
    ]

    crop = models.ForeignKey(
        'crops.Crop',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='pest_disease_profiles'
    )
    crop_name = models.CharField(max_length=100, db_index=True)
    pest_or_disease_name = models.CharField(max_length=150, db_index=True)
    pest_or_disease_name_gu = models.CharField(max_length=150, blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Fungal')
    risk_level = models.CharField(max_length=20, choices=RISK_CHOICES, default='Medium')

    # Weather trigger conditions for AI risk calculation
    min_temp_trigger = models.FloatField(default=20.0, help_text="Min temp in °C")
    max_temp_trigger = models.FloatField(default=35.0, help_text="Max temp in °C")
    min_humidity_trigger = models.FloatField(default=70.0, help_text="Min humidity % that triggers spread")
    rainfall_trigger = models.BooleanField(default=False, help_text="Whether rainfall/moisture spikes risk")

    symptoms = models.TextField()
    symptoms_gu = models.TextField(blank=True, null=True)
    prevention = models.TextField()
    prevention_gu = models.TextField(blank=True, null=True)
    management = models.TextField()
    management_gu = models.TextField(blank=True, null=True)
    source = models.CharField(max_length=150, default='Anand Agricultural University (AAU) Plant Pathology Department')
    data_source = models.CharField(max_length=150, default='Anand Agricultural University (AAU) Plant Pathology Department')
    data_type = models.CharField(max_length=50, default='Scientific Disease Profile')
    reference_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pest_disease_information'
        ordering = ['crop_name', 'pest_or_disease_name']
        indexes = [
            models.Index(fields=['crop_name', 'category']),
        ]

    def __str__(self):
        return f"{self.pest_or_disease_name} on {self.crop_name} ({self.category})"
