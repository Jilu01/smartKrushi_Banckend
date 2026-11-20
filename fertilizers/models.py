from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Fertilizer(models.Model):
    TYPE_CHOICES = [
        ('Chemical', 'Chemical / Synthetic Fertilizer'),
        ('Organic', 'Organic Fertilizer / Manure'),
        ('Bio-fertilizer', 'Bio-fertilizer / Microbial Inoculant'),
        ('Micronutrient', 'Micronutrient Fertilizer'),
        ('Water Soluble', 'Water Soluble / Fertigation'),
    ]

    fertilizer_name = models.CharField(max_length=150, unique=True, db_index=True)
    fertilizer_name_gujarati = models.CharField(max_length=150, blank=True, null=True, db_index=True)
    fertilizer_type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='Chemical', db_index=True)
    npk_ratio = models.CharField(max_length=50, blank=True, null=True, help_text="e.g. 46:0:0, 18:46:0, 0:0:60")

    # Nutrient composition percentages
    nitrogen_percentage = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="N percentage (%)"
    )
    phosphorus_percentage = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="P2O5 percentage (%)"
    )
    potassium_percentage = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="K2O percentage (%)"
    )
    sulphur_percentage = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="S percentage (%)"
    )
    micronutrient_composition = models.TextField(
        blank=True,
        null=True,
        help_text="e.g. Zinc: 21%, Boron: 0.5%, Iron: 1%"
    )

    recommended_crops = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Comma-separated crops or 'All crops', 'Cereals', 'Pulses', etc."
    )
    application_method = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="e.g. Basal broadcasting, Top dressing, Foliar spray, Drip fertigation"
    )
    application_stage = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="e.g. Basal (At Sowing), Vegetative Stage, Flowering"
    )
    dosage_per_hectare = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. 50-100 kg/ha")
    application_timing = models.CharField(max_length=200, blank=True, null=True, help_text="e.g. At sowing, 30 days after sowing")
    safety_instructions = models.TextField(blank=True, null=True)
    precautions = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    data_source = models.CharField(max_length=150, default='Fertilizer Association of India / AAU Anand')
    data_type = models.CharField(max_length=50, default='Standard Technical Specification')
    reference_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fertilizers'
        ordering = ['fertilizer_name']

    def __str__(self):
        npk = f"({self.nitrogen_percentage}-{self.phosphorus_percentage}-{self.potassium_percentage})"
        return f"{self.fertilizer_name} {npk} [{self.fertilizer_type}]"


# Architecture Master Alias
FertilizerMaster = Fertilizer


class FertilizerRecommendation(models.Model):
    crop = models.ForeignKey('crops.Crop', on_delete=models.CASCADE, null=True, blank=True, related_name='fertilizer_recommendation_records')
    crop_name = models.CharField(max_length=100, db_index=True)
    fertilizer = models.ForeignKey(Fertilizer, on_delete=models.CASCADE, related_name='recommendations')

    state = models.CharField(max_length=100, default='Gujarat')
    district = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    taluka = models.CharField(max_length=100, blank=True, null=True)
    village = models.CharField(max_length=100, blank=True, null=True)

    growth_stage = models.CharField(max_length=100, default='Basal Dose (At Sowing)')
    land_area = models.FloatField(default=1.0, help_text="Land area in hectares")
    recommended_quantity_per_ha = models.FloatField(help_text="Quantity in kg per hectare")
    total_quantity_farmer_land = models.FloatField(help_text="Total quantity in kg for farmer land area")

    application_timing = models.CharField(max_length=200, blank=True, null=True)
    application_method = models.CharField(max_length=150, default='Broadcasting / Side Dressing')
    number_of_applications = models.PositiveIntegerField(default=1)
    precautions = models.TextField(blank=True, null=True)
    recommendation_source = models.CharField(max_length=150, default='Anand Agricultural University (AAU) / Soil Health Card Scheme')
    data_source = models.CharField(max_length=150, default='Anand Agricultural University (AAU) / Soil Health Card Scheme')
    data_type = models.CharField(max_length=50, default='Agronomic Dosage Guideline')
    reference_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fertilizer_recommendations'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.fertilizer.fertilizer_name} for {self.crop_name} ({self.total_quantity_farmer_land} kg)"


# Architecture Master Alias
FertilizerApplicationGuide = FertilizerRecommendation
