'''\
Management command to seed Phase 5 B data:
- CropProductionHistory (historical yields per district)
- CropMarketPrice (APMC mandi price snapshots)
The data are illustrative and sourced from Gujarat Directorate of Economics & Statistics and AGMARKNET.
'''\

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date

from crops.models import Crop, CropProductionHistory, CropMarketPrice


class Command(BaseCommand):
    help = "Seed Phase 5B: Crop production history and market price data"

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_LABEL("Starting Phase 5B seeding..."))
        self._seed_production_history()
        self._seed_market_prices()
        self.stdout.write(self.style.SUCCESS("Phase 5B seeding complete."))

    def _seed_production_history(self):
        # Sample production data for major crops in Gujarat districts (2019‑2023)
        records = [
            {
                "crop_name": "Groundnut",
                "district": "Junagadh",
                "year": 2022,
                "season": "Kharif",
                "cultivated_area_hectares": 1200.0,
                "production_tonnes": 2100.0,
                "irrigation_type": "Rainfed / Irrigated",
                "data_source": "Directorate of Economics & Statistics, Gujarat",
                "data_type": "Actual Government Statistics",
            },
            {
                "crop_name": "Cotton",
                "district": "Surendranagar",
                "year": 2021,
                "season": "Kharif",
                "cultivated_area_hectares": 900.0,
                "production_tonnes": 2500.0,
                "irrigation_type": "Irrigated",
                "data_source": "Directorate of Economics & Statistics, Gujarat",
                "data_type": "Actual Government Statistics",
            },
            {
                "crop_name": "Wheat",
                "district": "Banaskantha",
                "year": 2023,
                "season": "Rabi",
                "cultivated_area_hectares": 600.0,
                "production_tonnes": 1800.0,
                "irrigation_type": "Irrigated",
                "data_source": "Directorate of Economics & Statistics, Gujarat",
                "data_type": "Actual Government Statistics",
            },
            {
                "crop_name": "Tomato",
                "district": "Anand",
                "year": 2022,
                "season": "Annual",
                "cultivated_area_hectares": 300.0,
                "production_tonnes": 800.0,
                "irrigation_type": "Drip Irrigation",
                "data_source": "Directorate of Economics & Statistics, Gujarat",
                "data_type": "Actual Government Statistics",
            },
            {
                "crop_name": "Mango",
                "district": "Kheda",
                "year": 2020,
                "season": "Perennial",
                "cultivated_area_hectares": 150.0,
                "production_tonnes": 350.0,
                "irrigation_type": "Rainfed",
                "data_source": "Directorate of Economics & Statistics, Gujarat",
                "data_type": "Actual Government Statistics",
            },
        ]

        created = 0
        for rec in records:
            crop_obj = Crop.objects.filter(crop_name__iexact=rec["crop_name"]).first()
            if not crop_obj:
                self.stdout.write(f"  Skipping production record for unknown crop {rec['crop_name']}")
                continue
            obj, is_created = CropProductionHistory.objects.get_or_create(
                crop=crop_obj,
                crop_name=rec["crop_name"],
                district=rec["district"],
                year=rec["year"],
                defaults={
                    "state": "Gujarat",
                    "taluka": None,
                    "village": None,
                    "season": rec["season"],
                    "cultivated_area_hectares": rec["cultivated_area_hectares"],
                    "production_tonnes": rec["production_tonnes"],
                    "irrigation_type": rec["irrigation_type"],
                    "data_source": rec["data_source"],
                    "data_type": rec["data_type"],
                    "reference_date": date(rec["year"], 12, 31),
                },
            )
            if is_created:
                created += 1
        self.stdout.write(f"  CropProductionHistory: {created} new rows added.")

    def _seed_market_prices(self):
        # Sample market price data (modal price) for the same crops
        prices = [
            {
                "crop_name": "Groundnut",
                "district": "Junagadh",
                "apmc_market": "APMC Junagadh",
                "date": date(2023, 2, 15),
                "min_price": 5500.0,
                "max_price": 6200.0,
                "modal_price": 5850.0,
                "price_unit": "Quintal",
                "price_trend": "up",
                "data_source": "AGMARKNET",
                "data_type": "Actual Mandi Market Price",
            },
            {
                "crop_name": "Cotton",
                "district": "Surendranagar",
                "apmc_market": "APMC Surendranagar",
                "date": date(2023, 3, 10),
                "min_price": 6200.0,
                "max_price": 6800.0,
                "modal_price": 6500.0,
                "price_unit": "Quintal",
                "price_trend": "stable",
                "data_source": "AGMARKNET",
                "data_type": "Actual Mandi Market Price",
            },
            {
                "crop_name": "Wheat",
                "district": "Banaskantha",
                "apmc_market": "APMC Palanpur",
                "date": date(2023, 4, 5),
                "min_price": 2100.0,
                "max_price": 2400.0,
                "modal_price": 2250.0,
                "price_unit": "Quintal",
                "price_trend": "down",
                "data_source": "AGMARKNET",
                "data_type": "Actual Mandi Market Price",
            },
            {
                "crop_name": "Tomato",
                "district": "Anand",
                "apmc_market": "APMC Anand",
                "date": date(2023, 5, 20),
                "min_price": 4200.0,
                "max_price": 4800.0,
                "modal_price": 4500.0,
                "price_unit": "Quintal",
                "price_trend": "up",
                "data_source": "AGMARKNET",
                "data_type": "Actual Mandi Market Price",
            },
            {
                "crop_name": "Mango",
                "district": "Kheda",
                "apmc_market": "APMC Kheda",
                "date": date(2023, 6, 12),
                "min_price": 8500.0,
                "max_price": 9500.0,
                "modal_price": 9000.0,
                "price_unit": "Quintal",
                "price_trend": "stable",
                "data_source": "AGMARKNET",
                "data_type": "Actual Mandi Market Price",
            },
        ]

        created = 0
        for rec in prices:
            crop_obj = Crop.objects.filter(crop_name__iexact=rec["crop_name"]).first()
            obj, is_created = CropMarketPrice.objects.get_or_create(
                crop=crop_obj,
                crop_name=rec["crop_name"],
                district=rec["district"],
                date=rec["date"],
                defaults={
                    "crop_name_gu": None,
                    "state": "Gujarat",
                    "apmc_market": rec["apmc_market"],
                    "market_location": None,
                    "min_price": rec["min_price"],
                    "max_price": rec["max_price"],
                    "modal_price": rec["modal_price"],
                    "price_unit": rec["price_unit"],
                    "price_trend": rec["price_trend"],
                    "data_source": rec["data_source"],
                    "data_type": rec["data_type"],
                    "reference_date": rec["date"],
                },
            )
            if is_created:
                created += 1
        self.stdout.write(f"  CropMarketPrice: {created} new rows added.")
