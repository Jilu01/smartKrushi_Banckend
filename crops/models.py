from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


# Preserved legacy CropData model
class CropData(models.Model):
    crop_record_id = models.AutoField(primary_key=True)
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    crop_name = models.CharField(max_length=100)
    growing_season = models.CharField(max_length=50)
    crop_duration_days = models.PositiveIntegerField()
    illustrative_yield_kg_ha = models.FloatField()

    def __str__(self):
        return f"{self.crop_name} - {self.district}"

    class Meta:
        db_table = 'crop_data'
        ordering = ['state', 'district', 'crop_name']


class CropCategory(models.Model):
    category_code = models.CharField(max_length=50, unique=True, db_index=True)
    category_name = models.CharField(max_length=100, unique=True)
    category_name_gujarati = models.CharField(max_length=150, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    icon_name = models.CharField(max_length=50, blank=True, null=True, help_text="e.g. wheat, carrot, leaf")
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'crop_categories'
        ordering = ['display_order', 'category_name']

    def __str__(self):
        if self.category_name_gujarati:
            return f"{self.category_name} ({self.category_name_gujarati})"
        return self.category_name


class Crop(models.Model):
    CATEGORY_CHOICES = [
        ('Cereal', 'Cereals'),
        ('Pulse', 'Pulses'),
        ('Oilseed', 'Oilseeds'),
        ('Vegetable', 'Vegetables'),
        ('Fruit', 'Fruits'),
        ('Spice', 'Spices & Condiments'),
        ('Cash Crop', 'Cash Crops'),
        ('Fodder', 'Fodder Crops'),
        ('Medicinal', 'Medicinal & Aromatic Crops'),
        ('Fiber', 'Fiber Crops'),
        ('Other', 'Other Crops'),
    ]

    SEASON_CHOICES = [
        ('Kharif', 'Kharif (Monsoon)'),
        ('Rabi', 'Rabi (Winter)'),
        ('Zaid', 'Zaid (Summer)'),
        ('Annual', 'Annual / Year-Round'),
        ('Perennial', 'Perennial'),
    ]

    DATA_TYPE_CHOICES = [
        ('Actual', 'Actual / Field Tested'),
        ('Estimated', 'Estimated / Agronomic Survey'),
        ('Scientific', 'Scientific / University Guidelines'),
    ]

    crop_name = models.CharField(max_length=100, unique=True, db_index=True)
    crop_name_gujarati = models.CharField(max_length=150, blank=True, null=True, db_index=True)
    scientific_name = models.CharField(max_length=150, blank=True, null=True)
    crop_category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Cereal', db_index=True)
    category = models.ForeignKey(CropCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='crops')
    crop_description = models.TextField(blank=True, null=True)
    growing_season = models.CharField(max_length=50, choices=SEASON_CHOICES, default='Kharif', db_index=True)
    crop_duration_days = models.PositiveIntegerField(default=120)

    # Calendar details
    sowing_months = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. June - July")
    harvesting_months = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. October - November")

    # Agronomic tolerances
    suitable_soil = models.CharField(max_length=255, default='Alluvial, Black soil, Sandy Loam')
    suitable_ph_min = models.FloatField(
        default=6.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(14.0)]
    )
    suitable_ph_max = models.FloatField(
        default=7.5,
        validators=[MinValueValidator(0.0), MaxValueValidator(14.0)]
    )
    temperature_min = models.FloatField(default=15.0, help_text="Minimum temperature in °C")
    temperature_max = models.FloatField(default=35.0, help_text="Maximum temperature in °C")
    rainfall_min = models.FloatField(default=400.0, help_text="Min rainfall in mm")
    rainfall_max = models.FloatField(default=1200.0, help_text="Max rainfall in mm")
    sunlight_requirement = models.CharField(max_length=100, default='Full Sun (6-8 hours daily)')

    # Water & nutrients
    water_requirement = models.CharField(
        max_length=50,
        choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')],
        default='Medium'
    )
    rainfall_requirement = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. 600-1000 mm")
    fertilizer_requirement = models.TextField(blank=True, null=True, help_text="Recommended N:P:K ratio or dosage")

    # Cultivation timeline
    sowing_period = models.CharField(max_length=100, blank=True, null=True)
    harvesting_period = models.CharField(max_length=100, blank=True, null=True)
    irrigation_method = models.CharField(max_length=100, blank=True, null=True)
    common_diseases = models.TextField(blank=True, null=True)

    image = models.ImageField(upload_to='crops/images/', blank=True, null=True)

    data_source = models.CharField(max_length=150, default='Anand Agricultural University / ICAR')
    data_type = models.CharField(max_length=50, choices=DATA_TYPE_CHOICES, default='Scientific')
    reference_date = models.DateField(null=True, blank=True, help_text="Date of university reference data")
    is_active = models.BooleanField(default=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'crops'
        ordering = ['crop_name']

    def __str__(self):
        name = self.crop_name_gujarati if self.crop_name_gujarati else self.crop_name
        return f"{self.crop_name} ({name}) - {self.crop_category}"


# Master alias
CropMaster = Crop


class CropSeasonCalendar(models.Model):
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='season_calendars')
    state = models.CharField(max_length=100, default='Gujarat', db_index=True)
    district = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    taluka = models.CharField(max_length=100, blank=True, null=True)
    village = models.CharField(max_length=100, blank=True, null=True)

    season = models.CharField(
        max_length=50,
        choices=[
            ('Kharif', 'Kharif (Monsoon)'),
            ('Rabi', 'Rabi (Winter)'),
            ('Zaid', 'Zaid (Summer)'),
            ('Summer', 'Summer'),
            ('Perennial', 'Perennial / Year-Round'),
        ],
        db_index=True
    )
    sowing_start_month = models.CharField(max_length=50, help_text="e.g. June")
    sowing_end_month = models.CharField(max_length=50, help_text="e.g. July")
    harvest_start_month = models.CharField(max_length=50, help_text="e.g. October")
    harvest_end_month = models.CharField(max_length=50, help_text="e.g. November")

    crop_duration_days = models.PositiveIntegerField(default=120)
    irrigation_requirement = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. 4-6 irrigations, drip recommended")
    recommended_sowing_conditions = models.TextField(blank=True, null=True)
    data_source = models.CharField(max_length=150, default='Anand Agricultural University (AAU) / Directorate of Agriculture Gujarat')
    data_type = models.CharField(max_length=50, default='Official University Calendar')
    reference_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'crop_season_calendars'
        ordering = ['district', 'season', 'crop__crop_name']
        indexes = [
            models.Index(fields=['state', 'district', 'season']),
            models.Index(fields=['crop', 'season']),
        ]

    def __str__(self):
        loc = self.district or self.state
        return f"{self.crop.crop_name} Calendar ({self.season}) - {loc}"

    @property
    def source(self):
        return self.data_source


class CropLocationSuitability(models.Model):
    SUITABILITY_CHOICES = [
        ('Highly Suitable', 'Highly Suitable (ઉત્તમ અનુકૂળ)'),
        ('Moderately Suitable', 'Moderately Suitable (મધ્યમ અનુકૂળ)'),
        ('Marginally Suitable', 'Marginally Suitable (સાધારણ અનુકૂળ)'),
        ('Not Recommended', 'Not Recommended (બિનઅનુકૂળ)'),
    ]

    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='location_suitabilities')
    state = models.CharField(max_length=100, default='Gujarat', db_index=True)
    district = models.CharField(max_length=100, db_index=True)
    taluka = models.CharField(max_length=100, blank=True, null=True, db_index=True)

    suitability_level = models.CharField(max_length=50, choices=SUITABILITY_CHOICES, default='Highly Suitable')
    suitability_score = models.FloatField(default=85.0, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)], help_text="Suitability score (0-100)")
    favorable_seasons = models.CharField(max_length=150, default='Kharif')
    recommended_soil_types = models.CharField(max_length=255, default='Black, Alluvial')
    irrigation_dependency = models.CharField(max_length=100, default='Medium')
    limiting_factors = models.TextField(blank=True, null=True, help_text="e.g. High salinity risk, waterlogging sensitivity")
    agronomic_advisory = models.TextField(blank=True, null=True, help_text="Specific advice for this district/region")

    data_source = models.CharField(max_length=150, default='Anand Agricultural University (AAU) Agro-Ecological Zones')
    data_type = models.CharField(max_length=50, default='Scientific Survey')
    reference_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'crop_location_suitabilities'
        ordering = ['district', '-suitability_score', 'crop__crop_name']
        unique_together = ('crop', 'state', 'district', 'taluka')
        indexes = [
            models.Index(fields=['state', 'district', 'suitability_level']),
            models.Index(fields=['crop', 'district']),
        ]

    def __str__(self):
        loc = self.taluka if self.taluka else self.district
        return f"{self.crop.crop_name} Suitability in {loc}: {self.suitability_level} ({self.suitability_score}%)"


class CropProductionHistory(models.Model):
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='production_history')
    crop_name = models.CharField(max_length=100, db_index=True)
    state = models.CharField(max_length=100, default='Gujarat', db_index=True)
    district = models.CharField(max_length=100, db_index=True)
    taluka = models.CharField(max_length=100, blank=True, null=True)
    village = models.CharField(max_length=100, blank=True, null=True)

    year = models.PositiveIntegerField(default=2024, db_index=True)
    season = models.CharField(max_length=50, default='Kharif', db_index=True)
    cultivated_area_hectares = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    production_tonnes = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    yield_kg_per_hectare = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    irrigation_type = models.CharField(max_length=100, default='Rainfed / Irrigated')
    data_source = models.CharField(max_length=150, default='Directorate of Economics & Statistics, Ministry of Agriculture')
    data_type = models.CharField(max_length=50, default='Actual Government Statistics')
    reference_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'crop_production_history'
        ordering = ['-year', 'district', 'crop_name']
        indexes = [
            models.Index(fields=['state', 'district', 'year']),
            models.Index(fields=['crop', 'year']),
        ]

    def __str__(self):
        return f"{self.crop_name} in {self.district} ({self.year}) - {self.yield_kg_per_hectare} kg/ha"

    def save(self, *args, **kwargs):
        if self.cultivated_area_hectares > 0 and self.production_tonnes > 0 and (not self.yield_kg_per_hectare or self.yield_kg_per_hectare == 0.0):
            self.yield_kg_per_hectare = round((self.production_tonnes * 1000.0) / self.cultivated_area_hectares, 2)
        super().save(*args, **kwargs)


class CropCost(models.Model):
    COST_UNIT_CHOICES = [
        ('per_hectare', 'Per Hectare (₹/ha)'),
        ('per_acre', 'Per Acre (₹/acre)'),
    ]

    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='cultivation_costs')
    state = models.CharField(max_length=100, default='Gujarat', db_index=True)
    district = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    taluka = models.CharField(max_length=100, blank=True, null=True)
    year = models.PositiveIntegerField(default=2024)
    land_area = models.FloatField(default=1.0, help_text="Land area in hectares for cost baseline")
    cost_unit = models.CharField(max_length=50, choices=COST_UNIT_CHOICES, default='per_hectare')

    # Granular expense breakdown (₹)
    seed_cost = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    fertilizer_cost = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    pesticide_cost = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    labour_cost = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    irrigation_cost = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    machinery_cost = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    transportation_cost = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    harvesting_cost = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    other_expenses = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    total_cultivation_cost = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])

    data_source = models.CharField(max_length=150, default='CACP / Anand Agricultural University Studies')
    data_type = models.CharField(max_length=50, default='Estimated Agronomic Cost')
    reference_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'crop_costs'
        ordering = ['crop__crop_name', '-year']
        indexes = [
            models.Index(fields=['crop', 'state', 'district']),
        ]

    def __str__(self):
        loc = self.district or self.state
        return f"{self.crop.crop_name} Cost in {loc} ({self.year}): ₹{self.total_cultivation_cost}/{self.cost_unit}"

    def calculate_total(self):
        return round(
            self.seed_cost +
            self.fertilizer_cost +
            self.pesticide_cost +
            self.labour_cost +
            self.irrigation_cost +
            self.machinery_cost +
            self.transportation_cost +
            self.harvesting_cost +
            self.other_expenses,
            2
        )

    def cost_per_acre(self):
        """1 hectare = 2.47105 acres"""
        if self.cost_unit == 'per_acre':
            return self.total_cultivation_cost
        return round(self.total_cultivation_cost / 2.47105, 2)

    def cost_per_hectare(self):
        if self.cost_unit == 'per_hectare':
            return self.total_cultivation_cost
        return round(self.total_cultivation_cost * 2.47105, 2)

    def save(self, *args, **kwargs):
        self.total_cultivation_cost = self.calculate_total()
        super().save(*args, **kwargs)


# Master alias
CropCultivationCost = CropCost


class CropMarketPrice(models.Model):
    TREND_CHOICES = [
        ('up', 'Upward / Rising (↑)'),
        ('down', 'Downward / Falling (↓)'),
        ('stable', 'Stable / Steady (→)'),
    ]

    crop = models.ForeignKey(Crop, on_delete=models.SET_NULL, null=True, blank=True, related_name='market_prices')
    crop_name = models.CharField(max_length=100, db_index=True)
    crop_name_gu = models.CharField(max_length=150, blank=True, null=True)
    state = models.CharField(max_length=100, default='Gujarat', db_index=True)
    district = models.CharField(max_length=100, db_index=True)
    apmc_market = models.CharField(max_length=150, db_index=True, help_text="e.g. APMC Rajkot, APMC Unjha")
    market_location = models.CharField(max_length=150, blank=True, null=True)
    date = models.DateField(db_index=True)

    min_price = models.FloatField(validators=[MinValueValidator(0.0)], help_text="₹ per unit")
    max_price = models.FloatField(validators=[MinValueValidator(0.0)], help_text="₹ per unit")
    modal_price = models.FloatField(validators=[MinValueValidator(0.0)], help_text="₹ per unit")
    price_unit = models.CharField(max_length=50, default='Quintal', help_text="Quintal (100 kg), 20 Kg (Mann), etc.")
    price_trend = models.CharField(max_length=20, choices=TREND_CHOICES, default='stable')

    data_source = models.CharField(max_length=150, default='AGMARKNET / Gujarat State Agricultural Marketing Board')
    data_type = models.CharField(max_length=50, default='Actual Mandi Market Price')
    reference_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'crop_market_prices'
        ordering = ['-date', 'district', 'crop_name']
        indexes = [
            models.Index(fields=['crop_name', 'district', 'date']),
            models.Index(fields=['apmc_market', 'date']),
        ]

    def __str__(self):
        return f"{self.crop_name} @ {self.apmc_market} ({self.date}): ₹{self.modal_price}/{self.price_unit}"


class CropRecord(models.Model):
    state = models.CharField(max_length=100, db_index=True)
    district = models.CharField(max_length=100, db_index=True)
    taluka = models.CharField(max_length=100, blank=True, null=True, db_index=True)

    crop = models.ForeignKey(Crop, on_delete=models.SET_NULL, null=True, blank=True, related_name='records')
    crop_name = models.CharField(max_length=100, db_index=True)

    growing_season = models.CharField(max_length=50, db_index=True)
    crop_duration_days = models.PositiveIntegerField(default=120)

    area_hectares = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    production_tonnes = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    yield_kg_per_hectare = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])

    year = models.PositiveIntegerField(default=2024, db_index=True)
    data_source = models.CharField(max_length=150, default='State Agriculture Department')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'crop_records'
        ordering = ['-year', 'state', 'district', 'crop_name']
        indexes = [
            models.Index(fields=['state', 'district', 'year']),
            models.Index(fields=['crop_name', 'growing_season']),
        ]

    def __str__(self):
        return f"{self.crop_name} in {self.district} ({self.year}) - {self.yield_kg_per_hectare} kg/ha"

    def save(self, *args, **kwargs):
        # Auto-compute yield if area and production are provided
        if self.area_hectares > 0 and self.production_tonnes > 0 and (not self.yield_kg_per_hectare or self.yield_kg_per_hectare == 0.0):
            self.yield_kg_per_hectare = round((self.production_tonnes * 1000.0) / self.area_hectares, 2)
        # Link to Crop model if available
        if not self.crop_id and self.crop_name:
            match = Crop.objects.filter(crop_name__iexact=self.crop_name).first()
            if match:
                self.crop = match
        super().save(*args, **kwargs)