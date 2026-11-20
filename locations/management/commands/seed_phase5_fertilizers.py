"""
Phase 5: Fertilizer Master Seeding
Seeds Fertilizer master data and FertilizerRecommendation records for major crop-district combinations.
Sources: ICAR, Gujarat Agriculture Dept, AAU (Anand Agricultural University), JAU (Junagadh Agricultural University)
Data Type: Scientific / Estimated
"""

from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = "Seed Phase 5: Fertilizer Master and Recommendation Data"

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting Phase 5: Fertilizer Master Seeding...")
        self._seed_fertilizers()
        self._seed_fertilizer_recommendations()
        self.stdout.write(self.style.SUCCESS("Phase 5 Fertilizer Seeding Complete!"))

    def _seed_fertilizers(self):
        from fertilizers.models import Fertilizer

        fertilizers = [
            # Chemical Fertilizers
            {
                "name": "Urea",
                "description": "Urea (46% N) – Most commonly used nitrogen fertilizer in India. Recommended for basal application.",
                "fertilizer_type": "Chemical",
                "npk_ratio": "46-0-0",
                "suitable_crops": "All crops",
                "application_method": "Broadcast or band placement",
                "application_timing": "Basal and top dressing",
                "quantity_per_hectare": "50-200 kg/ha depending on crop",
                "safety_instructions": "Apply when soil is moist. Avoid application before rain. Store in cool dry place.",
                "is_organic": False,
            },
            {
                "name": "DAP (Di-Ammonium Phosphate)",
                "description": "DAP (18:46:0) – High phosphorus fertilizer, used widely as basal fertilizer.",
                "fertilizer_type": "Chemical",
                "npk_ratio": "18-46-0",
                "suitable_crops": "All crops especially Wheat, Pulses, Oilseeds",
                "application_method": "Basal incorporation",
                "application_timing": "At sowing",
                "quantity_per_hectare": "50-150 kg/ha",
                "safety_instructions": "Do not mix with lime. Store in moisture-free conditions.",
                "is_organic": False,
            },
            {
                "name": "MOP (Muriate of Potash)",
                "description": "MOP (0:0:60) – Primary source of potassium. Improves crop quality and disease resistance.",
                "fertilizer_type": "Chemical",
                "npk_ratio": "0-0-60",
                "suitable_crops": "Cotton, Sugarcane, Potato, Banana, Fruits",
                "application_method": "Broadcast or furrow placement",
                "application_timing": "Basal or split application",
                "quantity_per_hectare": "30-100 kg/ha",
                "safety_instructions": "Avoid excessive application on saline soils.",
                "is_organic": False,
            },
            {
                "name": "SSP (Single Super Phosphate)",
                "description": "SSP (16:0:0 P2O5 + 11% S + 19% Ca) – Provides phosphorus, sulphur, and calcium. Ideal for groundnut and oilseeds.",
                "fertilizer_type": "Chemical",
                "npk_ratio": "0-16-0",
                "suitable_crops": "Groundnut, Mustard, Soybean, Sesame, Pulses",
                "application_method": "Basal incorporation",
                "application_timing": "At sowing",
                "quantity_per_hectare": "100-250 kg/ha",
                "safety_instructions": "Do not store in wet conditions.",
                "is_organic": False,
            },
            {
                "name": "NPK 10:26:26",
                "description": "Complex fertilizer with balanced NPK. Ideal for crops requiring high P and K.",
                "fertilizer_type": "Chemical",
                "npk_ratio": "10-26-26",
                "suitable_crops": "Cotton, Maize, Vegetables, Tomato",
                "application_method": "Broadcast or drip fertigation",
                "application_timing": "Basal application",
                "quantity_per_hectare": "100-200 kg/ha",
                "safety_instructions": "Store in cool dry area.",
                "is_organic": False,
            },
            {
                "name": "NPK 12:32:16",
                "description": "Complex NPK fertilizer for high-phosphorus demanding crops.",
                "fertilizer_type": "Chemical",
                "npk_ratio": "12-32-16",
                "suitable_crops": "Wheat, Pulses, Groundnut",
                "application_method": "Basal",
                "application_timing": "At sowing",
                "quantity_per_hectare": "100-150 kg/ha",
                "safety_instructions": "Avoid contact with eyes and skin.",
                "is_organic": False,
            },
            {
                "name": "Zinc Sulphate (ZnSO4)",
                "description": "Zinc micronutrient fertilizer. Zinc deficiency is widespread in Gujarat soils.",
                "fertilizer_type": "Micronutrient",
                "npk_ratio": "0-0-0",
                "suitable_crops": "Paddy, Wheat, Maize, Groundnut, Cotton, Vegetables",
                "application_method": "Soil application or foliar spray",
                "application_timing": "Basal or early vegetative stage",
                "quantity_per_hectare": "25 kg/ha soil; 0.5% foliar spray",
                "safety_instructions": "Do not mix with phosphate fertilizers.",
                "is_organic": False,
            },
            {
                "name": "Boron (Borax)",
                "description": "Boron micronutrient. Essential for fruit setting in groundnut, sugarcane, cotton.",
                "fertilizer_type": "Micronutrient",
                "npk_ratio": "0-0-0",
                "suitable_crops": "Groundnut, Cotton, Sugarcane, Fruits, Vegetables",
                "application_method": "Soil application or foliar spray",
                "application_timing": "At sowing or flowering stage",
                "quantity_per_hectare": "5-10 kg/ha borax soil; 0.2% foliar",
                "safety_instructions": "Do not over-apply; phytotoxic at high doses.",
                "is_organic": False,
            },
            {
                "name": "Ferrous Sulphate (FeSO4)",
                "description": "Iron micronutrient for iron-deficient calcareous soils of North Gujarat.",
                "fertilizer_type": "Micronutrient",
                "npk_ratio": "0-0-0",
                "suitable_crops": "Groundnut, Wheat, Soybean, Citrus, Vegetables",
                "application_method": "Soil application or foliar spray",
                "application_timing": "Early growth stage",
                "quantity_per_hectare": "25 kg/ha soil; 0.5% foliar spray",
                "safety_instructions": "May stain clothes and equipment.",
                "is_organic": False,
            },
            {
                "name": "FYM (Farm Yard Manure)",
                "description": "Organic manure from cattle dung. Improves soil structure, water holding capacity, and microbial activity.",
                "fertilizer_type": "Organic",
                "npk_ratio": "0.5-0.3-0.5",
                "suitable_crops": "All crops",
                "application_method": "Broadcast and incorporation",
                "application_timing": "15-30 days before sowing",
                "quantity_per_hectare": "5-10 tonnes/ha",
                "safety_instructions": "Use well-decomposed FYM only.",
                "is_organic": True,
            },
            {
                "name": "Vermicompost",
                "description": "Earthworm-processed organic compost. Rich in nutrients, plant growth hormones, and beneficial microbes.",
                "fertilizer_type": "Organic",
                "npk_ratio": "1.5-1.5-1.0",
                "suitable_crops": "Vegetables, Fruits, Flowers, Organic crops",
                "application_method": "Broadcast or band placement",
                "application_timing": "At sowing or transplanting",
                "quantity_per_hectare": "2-4 tonnes/ha",
                "safety_instructions": "Store in cool moist conditions.",
                "is_organic": True,
            },
            {
                "name": "Rhizobium Biofertilizer",
                "description": "Nitrogen-fixing bacteria inoculant for legume crops. Reduces nitrogen fertilizer requirement by 20-30 kg N/ha.",
                "fertilizer_type": "Biofertilizer",
                "npk_ratio": "0-0-0",
                "suitable_crops": "Groundnut, Chickpea, Pigeon Pea, Soybean, Cowpea, Green Gram, Black Gram",
                "application_method": "Seed treatment (250g/10 kg seed)",
                "application_timing": "Before sowing",
                "quantity_per_hectare": "250 g inoculant per 10 kg seed",
                "safety_instructions": "Do not expose to direct sunlight. Use within expiry date.",
                "is_organic": True,
            },
            {
                "name": "Azospirillum Biofertilizer",
                "description": "Nitrogen-fixing bacteria for cereal crops. Fixes 20-25 kg N/ha.",
                "fertilizer_type": "Biofertilizer",
                "npk_ratio": "0-0-0",
                "suitable_crops": "Bajra, Maize, Wheat, Jowar, Sugarcane, Paddy",
                "application_method": "Seed treatment or soil application",
                "application_timing": "At sowing",
                "quantity_per_hectare": "2-3 kg/ha for soil; 250g/10 kg seed",
                "safety_instructions": "Do not mix with pesticides or chemical fertilizers during application.",
                "is_organic": True,
            },
            {
                "name": "PSB (Phosphate Solubilizing Bacteria)",
                "description": "Microorganism that solubilizes fixed phosphorus in soil, making it available to crops.",
                "fertilizer_type": "Biofertilizer",
                "npk_ratio": "0-0-0",
                "suitable_crops": "All crops especially Groundnut, Wheat, Maize, Cotton",
                "application_method": "Seed treatment or soil application",
                "application_timing": "At sowing",
                "quantity_per_hectare": "2-3 kg/ha for soil; 250g/10 kg seed",
                "safety_instructions": "Use with organic matter for best results.",
                "is_organic": True,
            },
            {
                "name": "Neem Cake",
                "description": "By-product of neem oil extraction. Acts as organic fertilizer and soil pest repellent.",
                "fertilizer_type": "Organic",
                "npk_ratio": "4-1-1",
                "suitable_crops": "Groundnut, Cotton, Vegetables, Spices",
                "application_method": "Soil incorporation",
                "application_timing": "15-20 days before sowing",
                "quantity_per_hectare": "400-500 kg/ha",
                "safety_instructions": "Well-powdered form is more effective.",
                "is_organic": True,
            },
            {
                "name": "Sulphur (Bentonite Sulphur)",
                "description": "Sulphur fertilizer for groundnut, mustard, and onion. Improves oil content and crop quality.",
                "fertilizer_type": "Chemical",
                "npk_ratio": "0-0-0",
                "suitable_crops": "Groundnut, Mustard, Onion, Garlic, Pulses",
                "application_method": "Soil application",
                "application_timing": "Basal",
                "quantity_per_hectare": "20-40 kg/ha elemental sulphur",
                "safety_instructions": "Do not apply in acidic soils below pH 5.5.",
                "is_organic": False,
            },
            {
                "name": "Calcium Ammonium Nitrate (CAN)",
                "description": "Nitrogenous fertilizer with calcium. Good for acidic soils and vegetable crops.",
                "fertilizer_type": "Chemical",
                "npk_ratio": "25-0-0",
                "suitable_crops": "Vegetables, Fruits, Wheat",
                "application_method": "Top dressing",
                "application_timing": "During vegetative growth",
                "quantity_per_hectare": "100-200 kg/ha",
                "safety_instructions": "Do not store near combustible material.",
                "is_organic": False,
            },
            {
                "name": "Micronutrient Mix (Multi-Micronutrient)",
                "description": "Combined micronutrient fertilizer containing Zn, Fe, Mn, Cu, B, Mo. For general deficiency correction.",
                "fertilizer_type": "Micronutrient",
                "npk_ratio": "0-0-0",
                "suitable_crops": "All crops",
                "application_method": "Foliar spray or soil application",
                "application_timing": "Early vegetative to flowering stage",
                "quantity_per_hectare": "5-10 kg/ha soil; 2-3 kg/ha foliar",
                "safety_instructions": "Follow label recommendations for concentration.",
                "is_organic": False,
            },
            {
                "name": "Potassium Nitrate (KNO3)",
                "description": "Water-soluble fertilizer for fertigation and foliar spray. Provides N and K without chloride.",
                "fertilizer_type": "Chemical",
                "npk_ratio": "13-0-46",
                "suitable_crops": "Fruits, Vegetables, Potato, Grapes",
                "application_method": "Fertigation or foliar spray",
                "application_timing": "Fruit development stage",
                "quantity_per_hectare": "5 kg/ha foliar; 20-50 kg/ha fertigation",
                "safety_instructions": "Strong oxidizer; keep away from combustibles.",
                "is_organic": False,
            },
        ]

        created = 0
        updated = 0
        for f in fertilizers:
            obj, is_created = Fertilizer.objects.get_or_create(
                fertilizer_name=f["name"],
                defaults={
                    "description": f.get("description", ""),
                    "fertilizer_type": f.get("fertilizer_type", "Chemical"),
                    "npk_ratio": f.get("npk_ratio", ""),
                    # recommended_crops field stores comma-separated crop names
                    "recommended_crops": f.get("suitable_crops", ""),
                    "application_method": f.get("application_method", ""),
                    "application_stage": f.get("application_stage", ""),
                    "dosage_per_hectare": f.get("quantity_per_hectare", ""),
                    "application_timing": f.get("application_timing", ""),
                    "safety_instructions": f.get("safety_instructions", ""),
                    # micronutrient_composition can hold a simple string if needed
                },
            )
            if is_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(f"  Fertilizers: {created} created, {updated} already existed. Total: {Fertilizer.objects.count()}")

    def _seed_fertilizer_recommendations(self):
        from fertilizers.models import Fertilizer, FertilizerRecommendation
        from crops.models import Crop
        from locations.models import District

        # Major crop-district fertilizer recommendations for Gujarat
        # Source: AAU, JAU, ICAR recommendations
        recs = [
            # Groundnut - Junagadh (major groundnut belt)
            {
                "crop_name": "Groundnut",
                "district_name": "Junagadh",
                "fertilizer_name": "SSP (Single Super Phosphate)",
                "stage": "Basal",
                "dose_kg_per_hectare": 250.0,
                "application_method": "Broadcast and incorporation before sowing",
                "notes": "Provides P and S essential for groundnut. AAU recommendation: 25 kg P2O5/ha.",
                "data_source": "AAU Junagadh recommendation",
                "data_type": "Scientific",
            },
            {
                "crop_name": "Groundnut",
                "district_name": "Junagadh",
                "fertilizer_name": "Rhizobium Biofertilizer",
                "stage": "Seed Treatment",
                "dose_kg_per_hectare": 0.25,
                "application_method": "Seed treatment before sowing (250g/10 kg seed)",
                "notes": "Rhizobium strain NC-92 for groundnut. Reduces N fertilizer requirement.",
                "data_source": "ICAR recommendation",
                "data_type": "Scientific",
            },
            {
                "crop_name": "Groundnut",
                "district_name": "Junagadh",
                "fertilizer_name": "Zinc Sulphate (ZnSO4)",
                "stage": "Basal",
                "dose_kg_per_hectare": 25.0,
                "application_method": "Soil application before sowing",
                "notes": "Zinc deficiency common in Saurashtra soils. Apply once in 3 years.",
                "data_source": "AAU Gujarat recommendation",
                "data_type": "Scientific",
            },
            # Cotton - Surendranagar
            {
                "crop_name": "Cotton",
                "district_name": "Surendranagar",
                "fertilizer_name": "Urea",
                "stage": "Top Dressing",
                "dose_kg_per_hectare": 109.0,
                "application_method": "Split: 50% at 30 DAS, 50% at 60 DAS",
                "notes": "Recommended N dose for Bt Cotton: 50 kg N/ha = 109 kg Urea/ha",
                "data_source": "AAU Gujarat recommendation",
                "data_type": "Scientific",
            },
            {
                "crop_name": "Cotton",
                "district_name": "Surendranagar",
                "fertilizer_name": "DAP (Di-Ammonium Phosphate)",
                "stage": "Basal",
                "dose_kg_per_hectare": 54.0,
                "application_method": "Basal incorporation at sowing",
                "notes": "P dose for cotton: 25 kg P2O5/ha = 54 kg DAP/ha",
                "data_source": "AAU Gujarat recommendation",
                "data_type": "Scientific",
            },
            {
                "crop_name": "Cotton",
                "district_name": "Surendranagar",
                "fertilizer_name": "MOP (Muriate of Potash)",
                "stage": "Basal",
                "dose_kg_per_hectare": 83.0,
                "application_method": "Basal incorporation at sowing",
                "notes": "K dose for cotton: 50 kg K2O/ha = 83 kg MOP/ha",
                "data_source": "AAU Gujarat recommendation",
                "data_type": "Scientific",
            },
            # Cumin - Patan/Banaskantha
            {
                "crop_name": "Cumin",
                "district_name": "Patan",
                "fertilizer_name": "Urea",
                "stage": "Top Dressing",
                "dose_kg_per_hectare": 55.0,
                "application_method": "Split: at sowing and 30 DAS",
                "notes": "N dose for cumin: 25 kg N/ha = 55 kg Urea/ha",
                "data_source": "NRCSS/AAU recommendation",
                "data_type": "Scientific",
            },
            {
                "crop_name": "Cumin",
                "district_name": "Patan",
                "fertilizer_name": "DAP (Di-Ammonium Phosphate)",
                "stage": "Basal",
                "dose_kg_per_hectare": 54.0,
                "application_method": "Basal at sowing",
                "notes": "P dose: 25 kg P2O5/ha",
                "data_source": "NRCSS recommendation",
                "data_type": "Scientific",
            },
            # Wheat - Banaskantha
            {
                "crop_name": "Wheat",
                "district_name": "Banaskantha",
                "fertilizer_name": "Urea",
                "stage": "Top Dressing",
                "dose_kg_per_hectare": 196.0,
                "application_method": "1/3 basal + 1/3 at CRI stage + 1/3 at tillering",
                "notes": "N dose for irrigated wheat: 90 kg N/ha = 196 kg Urea/ha",
                "data_source": "ICAR-IIWR recommendation for Gujarat",
                "data_type": "Scientific",
            },
            {
                "crop_name": "Wheat",
                "district_name": "Banaskantha",
                "fertilizer_name": "DAP (Di-Ammonium Phosphate)",
                "stage": "Basal",
                "dose_kg_per_hectare": 109.0,
                "application_method": "Full dose basal at sowing",
                "notes": "P dose: 50 kg P2O5/ha = 109 kg DAP/ha",
                "data_source": "ICAR recommendation",
                "data_type": "Scientific",
            },
            # Bajra - Surendranagar/Mehsana
            {
                "crop_name": "Bajra",
                "district_name": "Mehsana",
                "fertilizer_name": "Urea",
                "stage": "Top Dressing",
                "dose_kg_per_hectare": 109.0,
                "application_method": "1/2 basal + 1/2 at 30 DAS",
                "notes": "N dose for Bajra: 50 kg N/ha = 109 kg Urea/ha",
                "data_source": "ICAR-IIMR recommendation",
                "data_type": "Scientific",
            },
            # Tomato - Anand
            {
                "crop_name": "Tomato",
                "district_name": "Anand",
                "fertilizer_name": "NPK 10:26:26",
                "stage": "Basal",
                "dose_kg_per_hectare": 150.0,
                "application_method": "Basal incorporation before transplanting",
                "notes": "Complex fertilizer for tomato: provides balanced P and K",
                "data_source": "AAU Anand recommendation",
                "data_type": "Scientific",
            },
            {
                "crop_name": "Tomato",
                "district_name": "Anand",
                "fertilizer_name": "Urea",
                "stage": "Top Dressing",
                "dose_kg_per_hectare": 218.0,
                "application_method": "3-4 split doses during crop growth",
                "notes": "N dose: 100 kg N/ha = 218 kg Urea/ha",
                "data_source": "AAU Anand recommendation",
                "data_type": "Scientific",
            },
            # Sugarcane - South Gujarat
            {
                "crop_name": "Sugarcane",
                "district_name": "Surat",
                "fertilizer_name": "Urea",
                "stage": "Top Dressing",
                "dose_kg_per_hectare": 435.0,
                "application_method": "Split: at planting, 60 DAS, 90 DAS, 120 DAS",
                "notes": "N dose for sugarcane: 200 kg N/ha = 435 kg Urea/ha",
                "data_source": "SBI/ICAR recommendation",
                "data_type": "Scientific",
            },
            {
                "crop_name": "Sugarcane",
                "district_name": "Surat",
                "fertilizer_name": "FYM (Farm Yard Manure)",
                "stage": "Basal",
                "dose_kg_per_hectare": 10000.0,
                "application_method": "Incorporate in soil before planting",
                "notes": "10 tonnes/ha well-decomposed FYM",
                "data_source": "SBI recommendation",
                "data_type": "Scientific",
            },
            # Mustard - Banaskantha
            {
                "crop_name": "Mustard",
                "district_name": "Banaskantha",
                "fertilizer_name": "Urea",
                "stage": "Top Dressing",
                "dose_kg_per_hectare": 87.0,
                "application_method": "1/2 basal + 1/2 at first irrigation",
                "notes": "N dose for mustard: 40 kg N/ha",
                "data_source": "NRCRM/ICAR recommendation",
                "data_type": "Scientific",
            },
            {
                "crop_name": "Mustard",
                "district_name": "Banaskantha",
                "fertilizer_name": "Sulphur (Bentonite Sulphur)",
                "stage": "Basal",
                "dose_kg_per_hectare": 40.0,
                "application_method": "Soil application before sowing",
                "notes": "Sulphur deficiency common in North Gujarat. Improves oil content.",
                "data_source": "ICAR recommendation",
                "data_type": "Scientific",
            },
            # Onion - Bhavnagar / Rajkot
            {
                "crop_name": "Onion",
                "district_name": "Bhavnagar",
                "fertilizer_name": "Urea",
                "stage": "Top Dressing",
                "dose_kg_per_hectare": 196.0,
                "application_method": "Split in 3 doses at 30, 45, 60 DAT",
                "notes": "N dose for Onion: 90 kg N/ha",
                "data_source": "NHRDF/ICAR recommendation",
                "data_type": "Scientific",
            },
            {
                "crop_name": "Onion",
                "district_name": "Bhavnagar",
                "fertilizer_name": "SSP (Single Super Phosphate)",
                "stage": "Basal",
                "dose_kg_per_hectare": 375.0,
                "application_method": "Basal before transplanting",
                "notes": "P dose: 60 kg P2O5/ha; SSP also provides sulphur important for pungency",
                "data_source": "NHRDF recommendation",
                "data_type": "Scientific",
            },
            # Castor - Saurashtra
            {
                "crop_name": "Castor",
                "district_name": "Rajkot",
                "fertilizer_name": "Urea",
                "stage": "Top Dressing",
                "dose_kg_per_hectare": 87.0,
                "application_method": "50% at sowing + 50% at 30 DAS",
                "notes": "N dose for castor: 40 kg N/ha = 87 kg Urea/ha",
                "data_source": "ICAR-AINP Castor recommendation",
                "data_type": "Scientific",
            },
            # Isabgol - Banaskantha/Patan
            {
                "crop_name": "Isabgol",
                "district_name": "Patan",
                "fertilizer_name": "DAP (Di-Ammonium Phosphate)",
                "stage": "Basal",
                "dose_kg_per_hectare": 54.0,
                "application_method": "Basal at sowing",
                "notes": "P dose: 25 kg P2O5/ha. Isabgol is a low-input crop.",
                "data_source": "NRCO/ICAR recommendation",
                "data_type": "Scientific",
            },
        ]

        created = 0
        skipped = 0
        for rec in recs:
            try:
                crop = Crop.objects.filter(crop_name__icontains=rec["crop_name"]).first()
                if not crop:
                    skipped += 1
                    continue

                district = District.objects.filter(district_name__icontains=rec["district_name"]).first()
                fertilizer = Fertilizer.objects.filter(name__icontains=rec["fertilizer_name"].split("(")[0].strip()).first()
                if not fertilizer:
                    # Try exact name
                    fertilizer = Fertilizer.objects.filter(name=rec["fertilizer_name"]).first()
                if not fertilizer:
                    skipped += 1
                    continue

                obj, is_created = FertilizerRecommendation.objects.get_or_create(
                    crop=crop,
                    fertilizer=fertilizer,
                    stage=rec["stage"],
                    defaults={
                        "dose_kg_per_hectare": rec["dose_kg_per_hectare"],
                        "application_method": rec.get("application_method", ""),
                        "notes": rec.get("notes", ""),
                        "data_source": rec.get("data_source", "ICAR"),
                        "data_type": rec.get("data_type", "Scientific"),
                    },
                )
                if is_created:
                    created += 1
                else:
                    skipped += 1
            except Exception as e:
                self.stdout.write(f"  Warning: {rec['crop_name']} - {e}")
                skipped += 1

        self.stdout.write(
            f"  FertilizerRecommendations: {created} created, {skipped} skipped. Total: {FertilizerRecommendation.objects.count()}"
        )
