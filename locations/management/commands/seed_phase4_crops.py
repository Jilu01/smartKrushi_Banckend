"""
Phase 4: Comprehensive Crop Master Data Seed
Covers all 9 categories: Cereals, Pulses, Oilseeds, Vegetables, Fruits,
Spices, Cash Crops, Fodder, Medicinal
Data Source: AAU (Anand Agricultural University), JAU, ICAR, Gujarat Dept of Agriculture
Data Type: Scientific / University Guidelines
"""
import datetime
from django.core.management.base import BaseCommand
from crops.models import Crop, CropCategory, CropSeasonCalendar, CropLocationSuitability


class Command(BaseCommand):
    help = "Seeds comprehensive Gujarat crop master data across 9 categories with season calendars and location suitability"

    def handle(self, *args, **options):
        self.stdout.write("Starting Phase 4: Crop Master Data Seeding...")

        # --- STEP 1: Seed CropCategories ---
        CATEGORIES = [
            {"code": "Cereal",    "name": "Cereals",                    "name_gu": "અનાજ પાક",         "icon": "wheat",   "order": 1},
            {"code": "Pulse",     "name": "Pulses",                     "name_gu": "કઠોળ પાક",          "icon": "bean",    "order": 2},
            {"code": "Oilseed",   "name": "Oilseeds",                   "name_gu": "તેલીબિયાં પાક",    "icon": "oil",     "order": 3},
            {"code": "Vegetable", "name": "Vegetables",                 "name_gu": "શાકભાજી",           "icon": "carrot",  "order": 4},
            {"code": "Fruit",     "name": "Fruits",                     "name_gu": "ફળ પાક",            "icon": "mango",   "order": 5},
            {"code": "Spice",     "name": "Spices & Condiments",        "name_gu": "મસાલા પાક",         "icon": "spice",   "order": 6},
            {"code": "Cash Crop", "name": "Cash Crops",                 "name_gu": "રોકડિયા પાક",       "icon": "cotton",  "order": 7},
            {"code": "Fodder",    "name": "Fodder Crops",               "name_gu": "ઘાસચારો",           "icon": "grass",   "order": 8},
            {"code": "Medicinal", "name": "Medicinal & Aromatic Crops", "name_gu": "ઔષધીય પાક",        "icon": "herb",    "order": 9},
            {"code": "Fiber",     "name": "Fiber Crops",                "name_gu": "રેસા પાક",          "icon": "fiber",   "order": 10},
        ]
        for c in CATEGORIES:
            obj, created = CropCategory.objects.get_or_create(
                category_code=c["code"],
                defaults={
                    "category_name": c["name"],
                    "category_name_gujarati": c["name_gu"],
                    "icon_name": c["icon"],
                    "display_order": c["order"],
                    "description": c["name"] + " grown in Gujarat"
                }
            )
            if not created and not obj.category_name_gujarati:
                obj.category_name_gujarati = c["name_gu"]
                obj.save()
        self.stdout.write(f"  Categories: {CropCategory.objects.count()} seeded.")

        # Helper: get category FK
        def cat(code):
            return CropCategory.objects.filter(category_code=code).first()

        # --- STEP 2: Comprehensive Crop Master Data ---
        SRC = "Anand Agricultural University (AAU) / ICAR Guidelines"
        REF = datetime.date(2024, 1, 1)

        CROPS = [
            # ============ CEREALS ============
            {
                "crop_name": "Bajra (Pearl Millet)",       "crop_name_gujarati": "બાજરો",
                "scientific_name": "Pennisetum glaucum",   "crop_category": "Cereal",
                "growing_season": "Kharif",                "crop_duration_days": 75,
                "sowing_months": "June - July",            "harvesting_months": "September - October",
                "suitable_soil": "Sandy Loam, Red, Black", "suitable_ph_min": 6.0, "suitable_ph_max": 7.5,
                "temperature_min": 25, "temperature_max": 42, "rainfall_min": 300, "rainfall_max": 700,
                "water_requirement": "Low", "sunlight_requirement": "Full Sun (8-10 hours)",
                "fertilizer_requirement": "N:P:K - 60:30:30 kg/ha basal + 30 kg N top dressing",
                "sowing_period": "June 15 - July 15", "harvesting_period": "September - October",
                "irrigation_method": "Drip/Furrow - 3-4 irrigations", "common_diseases": "Downy Mildew, Ergot, Smut",
                "crop_description": "Drought-tolerant cereal, main kharif crop of Saurashtra and North Gujarat. High water-use efficiency.",
            },
            {
                "crop_name": "Wheat",                      "crop_name_gujarati": "ઘઉં",
                "scientific_name": "Triticum aestivum",    "crop_category": "Cereal",
                "growing_season": "Rabi",                  "crop_duration_days": 120,
                "sowing_months": "November - December",    "harvesting_months": "March - April",
                "suitable_soil": "Alluvial, Black, Clay Loam", "suitable_ph_min": 6.0, "suitable_ph_max": 7.5,
                "temperature_min": 10, "temperature_max": 25, "rainfall_min": 400, "rainfall_max": 1000,
                "water_requirement": "Medium", "sunlight_requirement": "Full Sun (8 hours)",
                "fertilizer_requirement": "N:P:K - 120:60:40 kg/ha",
                "sowing_period": "November 15 - December 15", "harvesting_period": "March - April",
                "irrigation_method": "Flood/Sprinkler - 4-6 irrigations", "common_diseases": "Rust, Loose Smut, Karnal Bunt",
                "crop_description": "Major rabi cereal of North and Central Gujarat. Requires cool weather for good grain set.",
            },
            {
                "crop_name": "Paddy (Rice)",               "crop_name_gujarati": "ડાંગર",
                "scientific_name": "Oryza sativa",         "crop_category": "Cereal",
                "growing_season": "Kharif",                "crop_duration_days": 130,
                "sowing_months": "June - July",            "harvesting_months": "October - November",
                "suitable_soil": "Clay Loam, Black",       "suitable_ph_min": 5.5, "suitable_ph_max": 7.0,
                "temperature_min": 20, "temperature_max": 38, "rainfall_min": 1000, "rainfall_max": 2000,
                "water_requirement": "High", "sunlight_requirement": "Full Sun (8-10 hours)",
                "fertilizer_requirement": "N:P:K - 100:50:50 kg/ha",
                "sowing_period": "June - July (transplanting June 20 - July 20)", "harvesting_period": "October - November",
                "irrigation_method": "Flooded paddy field, 3-5 cm standing water", "common_diseases": "Blast, BLB, Sheath Rot, Brown Plant Hopper",
                "crop_description": "Grown in South Gujarat (Valsad, Navsari, Surat) and Dang. Requires flooded conditions and high rainfall.",
            },
            {
                "crop_name": "Maize",                      "crop_name_gujarati": "મકાઈ",
                "scientific_name": "Zea mays",             "crop_category": "Cereal",
                "growing_season": "Kharif",                "crop_duration_days": 100,
                "sowing_months": "June - July",            "harvesting_months": "September - October",
                "suitable_soil": "Sandy Loam, Alluvial, Red", "suitable_ph_min": 5.8, "suitable_ph_max": 7.0,
                "temperature_min": 18, "temperature_max": 35, "rainfall_min": 500, "rainfall_max": 1200,
                "water_requirement": "Medium", "sunlight_requirement": "Full Sun (8 hours)",
                "fertilizer_requirement": "N:P:K - 150:75:50 kg/ha",
                "sowing_period": "June 15 - July 15", "harvesting_period": "September - October",
                "irrigation_method": "Drip/Furrow - 5-6 irrigations", "common_diseases": "Fall Armyworm, Stalk Rot, Leaf Blight",
                "crop_description": "Multipurpose cereal for food, feed and industrial use. Major crop in Panchmahal, Dahod, Sabarkantha.",
            },
            {
                "crop_name": "Jowar (Sorghum)",            "crop_name_gujarati": "જુવાર",
                "scientific_name": "Sorghum bicolor",      "crop_category": "Cereal",
                "growing_season": "Kharif",                "crop_duration_days": 110,
                "sowing_months": "June - July",            "harvesting_months": "October - November",
                "suitable_soil": "Black, Sandy Loam",      "suitable_ph_min": 6.0, "suitable_ph_max": 7.5,
                "temperature_min": 25, "temperature_max": 40, "rainfall_min": 400, "rainfall_max": 1000,
                "water_requirement": "Low", "sunlight_requirement": "Full Sun (8-10 hours)",
                "fertilizer_requirement": "N:P:K - 80:40:40 kg/ha",
                "sowing_period": "June - July", "harvesting_period": "October - November",
                "irrigation_method": "Rainfed / 2-3 irrigations", "common_diseases": "Head Smut, Downy Mildew, Shoot Fly",
                "crop_description": "Drought-tolerant cereal for food and fodder. Major in Surendranagar, Bhavnagar, Amreli.",
            },
            {
                "crop_name": "Barley",                     "crop_name_gujarati": "જવ",
                "scientific_name": "Hordeum vulgare",      "crop_category": "Cereal",
                "growing_season": "Rabi",                  "crop_duration_days": 100,
                "sowing_months": "November - December",    "harvesting_months": "March",
                "suitable_soil": "Sandy Loam, Alluvial",   "suitable_ph_min": 6.0, "suitable_ph_max": 8.0,
                "temperature_min": 7, "temperature_max": 22, "rainfall_min": 300, "rainfall_max": 800,
                "water_requirement": "Low", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 60:30:20 kg/ha",
                "sowing_period": "November - December", "harvesting_period": "March - April",
                "irrigation_method": "2-3 irrigations", "common_diseases": "Yellow Rust, Powdery Mildew, Net Blotch",
                "crop_description": "Cold-tolerant rabi cereal. Used for malt, animal feed. Grown in North Gujarat.",
            },
            {
                "crop_name": "Ragi (Finger Millet)",       "crop_name_gujarati": "નાગલી",
                "scientific_name": "Eleusine coracana",    "crop_category": "Cereal",
                "growing_season": "Kharif",                "crop_duration_days": 115,
                "sowing_months": "June - July",            "harvesting_months": "October - November",
                "suitable_soil": "Sandy Loam, Red",        "suitable_ph_min": 5.5, "suitable_ph_max": 7.5,
                "temperature_min": 20, "temperature_max": 35, "rainfall_min": 700, "rainfall_max": 1500,
                "water_requirement": "Low", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 60:30:30 kg/ha",
                "sowing_period": "June - July", "harvesting_period": "October - November",
                "irrigation_method": "Rainfed - 2-3 irrigations", "common_diseases": "Blast, Brown Spot",
                "crop_description": "Nutritious millet high in calcium. Grown in tribal areas of Dang, Panchmahal, Chhota Udaipur.",
            },
            # ============ PULSES ============
            {
                "crop_name": "Chickpea (Gram)",            "crop_name_gujarati": "ચણા",
                "scientific_name": "Cicer arietinum",      "crop_category": "Pulse",
                "growing_season": "Rabi",                  "crop_duration_days": 110,
                "sowing_months": "October - November",     "harvesting_months": "February - March",
                "suitable_soil": "Sandy Loam, Black",      "suitable_ph_min": 6.0, "suitable_ph_max": 8.0,
                "temperature_min": 10, "temperature_max": 28, "rainfall_min": 400, "rainfall_max": 700,
                "water_requirement": "Low", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 20:50:30 kg/ha (Rhizobium inoculant)",
                "sowing_period": "October 15 - November 30", "harvesting_period": "February - March",
                "irrigation_method": "Rainfed / 1-2 protective irrigations", "common_diseases": "Botrytis Gray Mold, Wilt, Collar Rot",
                "crop_description": "Major winter pulse in Gujarat. Nitrogen-fixing legume. Grown extensively in Banaskantha, Patan, Surendranagar.",
            },
            {
                "crop_name": "Pigeon Pea (Tur/Arhar)",    "crop_name_gujarati": "તુવેર",
                "scientific_name": "Cajanus cajan",        "crop_category": "Pulse",
                "growing_season": "Kharif",                "crop_duration_days": 160,
                "sowing_months": "June - July",            "harvesting_months": "December - January",
                "suitable_soil": "Sandy Loam, Black",      "suitable_ph_min": 6.0, "suitable_ph_max": 7.5,
                "temperature_min": 20, "temperature_max": 35, "rainfall_min": 600, "rainfall_max": 1000,
                "water_requirement": "Low", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 25:50:25 kg/ha",
                "sowing_period": "June 15 - July 15", "harvesting_period": "December - January",
                "irrigation_method": "Rainfed / 2-3 irrigations", "common_diseases": "Wilt, Sterility Mosaic, Pod Borer",
                "crop_description": "Long-duration kharif pulse. High protein, drought-tolerant. Major crop in South and Central Gujarat.",
            },
            {
                "crop_name": "Green Gram (Moong)",         "crop_name_gujarati": "મગ",
                "scientific_name": "Vigna radiata",        "crop_category": "Pulse",
                "growing_season": "Kharif",                "crop_duration_days": 65,
                "sowing_months": "June - July",            "harvesting_months": "August - September",
                "suitable_soil": "Sandy Loam, Alluvial",   "suitable_ph_min": 6.0, "suitable_ph_max": 7.5,
                "temperature_min": 25, "temperature_max": 35, "rainfall_min": 500, "rainfall_max": 900,
                "water_requirement": "Low", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 20:40:20 kg/ha",
                "sowing_period": "June - July", "harvesting_period": "August - September",
                "irrigation_method": "2-3 irrigations", "common_diseases": "Yellow Mosaic Virus, Powdery Mildew, Root Rot",
                "crop_description": "Short-duration summer and kharif pulse. High nutrition. Grown across Gujarat in short rotation.",
            },
            {
                "crop_name": "Black Gram (Urad)",          "crop_name_gujarati": "અડદ",
                "scientific_name": "Vigna mungo",          "crop_category": "Pulse",
                "growing_season": "Kharif",                "crop_duration_days": 75,
                "sowing_months": "June - July",            "harvesting_months": "September - October",
                "suitable_soil": "Sandy Loam, Clay Loam",  "suitable_ph_min": 6.0, "suitable_ph_max": 7.5,
                "temperature_min": 25, "temperature_max": 35, "rainfall_min": 600, "rainfall_max": 900,
                "water_requirement": "Low", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 20:40:20 kg/ha",
                "sowing_period": "June - July", "harvesting_period": "September - October",
                "irrigation_method": "2-3 irrigations", "common_diseases": "Yellow Mosaic Virus, Leaf Spot",
                "crop_description": "Kharif pulse rich in protein. Used for dal and papad. Grown in South and Central Gujarat.",
            },
            {
                "crop_name": "Cowpea",                     "crop_name_gujarati": "ચોળા",
                "scientific_name": "Vigna unguiculata",    "crop_category": "Pulse",
                "growing_season": "Kharif",                "crop_duration_days": 70,
                "sowing_months": "June - July",            "harvesting_months": "September",
                "suitable_soil": "Sandy Loam, Red",        "suitable_ph_min": 5.5, "suitable_ph_max": 7.5,
                "temperature_min": 25, "temperature_max": 38, "rainfall_min": 400, "rainfall_max": 1000,
                "water_requirement": "Low", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 20:40:20 kg/ha",
                "sowing_period": "June - July", "harvesting_period": "August - September",
                "irrigation_method": "Rainfed / 2 irrigations", "common_diseases": "Mosaic Virus, Powdery Mildew, Aphids",
                "crop_description": "Heat and drought-tolerant pulse. Used as green vegetable, dal and cover crop.",
            },
            {
                "crop_name": "Moth Bean",                  "crop_name_gujarati": "મઠ",
                "scientific_name": "Vigna aconitifolia",   "crop_category": "Pulse",
                "growing_season": "Kharif",                "crop_duration_days": 75,
                "sowing_months": "July",                   "harvesting_months": "September - October",
                "suitable_soil": "Sandy, Sandy Loam",      "suitable_ph_min": 6.5, "suitable_ph_max": 8.0,
                "temperature_min": 28, "temperature_max": 42, "rainfall_min": 200, "rainfall_max": 500,
                "water_requirement": "Low", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 15:30:15 kg/ha",
                "sowing_period": "July - August", "harvesting_period": "September - October",
                "irrigation_method": "Rainfed (extreme drought tolerant)", "common_diseases": "Yellow Mosaic Virus, Leaf Crinkle",
                "crop_description": "Extremely drought-tolerant arid zone pulse. Grown in Kutch and North Gujarat dry tracts.",
            },
            {
                "crop_name": "Lentil (Masoor)",            "crop_name_gujarati": "મસૂર",
                "scientific_name": "Lens culinaris",       "crop_category": "Pulse",
                "growing_season": "Rabi",                  "crop_duration_days": 115,
                "sowing_months": "November",               "harvesting_months": "March",
                "suitable_soil": "Sandy Loam, Alluvial",   "suitable_ph_min": 6.0, "suitable_ph_max": 7.5,
                "temperature_min": 7, "temperature_max": 22, "rainfall_min": 400, "rainfall_max": 800,
                "water_requirement": "Low", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 20:40:20 kg/ha",
                "sowing_period": "November - December", "harvesting_period": "February - March",
                "irrigation_method": "1-2 protective irrigations", "common_diseases": "Rust, Collar Rot, Stemphylium Blight",
                "crop_description": "Cool-season pulse. High protein and iron content. Grown in North and Central Gujarat rabi season.",
            },
            # ============ OILSEEDS ============
            {
                "crop_name": "Groundnut",                  "crop_name_gujarati": "મગફળી",
                "scientific_name": "Arachis hypogaea",     "crop_category": "Oilseed",
                "growing_season": "Kharif",                "crop_duration_days": 120,
                "sowing_months": "June - July",            "harvesting_months": "October - November",
                "suitable_soil": "Sandy Loam, Red",        "suitable_ph_min": 6.0, "suitable_ph_max": 7.0,
                "temperature_min": 22, "temperature_max": 35, "rainfall_min": 500, "rainfall_max": 1200,
                "water_requirement": "Medium", "sunlight_requirement": "Full Sun (8-10 hours)",
                "fertilizer_requirement": "N:P:K - 25:50:50 kg/ha + Gypsum 400 kg/ha at pegging",
                "sowing_period": "June 15 - July 15", "harvesting_period": "October - November",
                "irrigation_method": "Drip/Sprinkler - 4-5 irrigations", "common_diseases": "Tikka Leaf Spot, Collar Rot, Bud Necrosis, White Grub",
                "crop_description": "Most important kharif oilseed of Gujarat. #1 groundnut state in India. Major in Saurashtra (Junagadh, Rajkot, Amreli).",
            },
            {
                "crop_name": "Castor",                     "crop_name_gujarati": "એરંડા",
                "scientific_name": "Ricinus communis",     "crop_category": "Oilseed",
                "growing_season": "Kharif",                "crop_duration_days": 180,
                "sowing_months": "June - July",            "harvesting_months": "December - January",
                "suitable_soil": "Sandy Loam, Red, Black", "suitable_ph_min": 5.5, "suitable_ph_max": 7.5,
                "temperature_min": 20, "temperature_max": 38, "rainfall_min": 500, "rainfall_max": 1000,
                "water_requirement": "Low", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 60:30:30 kg/ha",
                "sowing_period": "June - July", "harvesting_period": "December - February",
                "irrigation_method": "Drip/Furrow - 4-6 irrigations", "common_diseases": "Seedling Blight, Gray Mold, Phytoplasma Wilt",
                "crop_description": "Gujarat accounts for 90%+ of India's castor production. Major industrial oilseed crop. Mehsana, Banaskantha, Bhavnagar are top producing districts.",
            },
            {
                "crop_name": "Mustard",                    "crop_name_gujarati": "રાઈ / સરસવ",
                "scientific_name": "Brassica juncea",      "crop_category": "Oilseed",
                "growing_season": "Rabi",                  "crop_duration_days": 110,
                "sowing_months": "October - November",     "harvesting_months": "February - March",
                "suitable_soil": "Alluvial, Sandy Loam",   "suitable_ph_min": 6.0, "suitable_ph_max": 7.5,
                "temperature_min": 7, "temperature_max": 25, "rainfall_min": 400, "rainfall_max": 1000,
                "water_requirement": "Low", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 100:50:30 kg/ha + Sulphur 20 kg/ha",
                "sowing_period": "October 15 - November 15", "harvesting_period": "February - March",
                "irrigation_method": "3-4 irrigations", "common_diseases": "Alternaria Blight, Powdery Mildew, Aphids",
                "crop_description": "Main rabi oilseed of North Gujarat. High oil content (40-42%). Grown in Banaskantha, Patan, Mehsana.",
            },
            {
                "crop_name": "Sesame (Til)",               "crop_name_gujarati": "તલ",
                "scientific_name": "Sesamum indicum",      "crop_category": "Oilseed",
                "growing_season": "Kharif",                "crop_duration_days": 85,
                "sowing_months": "June - July",            "harvesting_months": "September - October",
                "suitable_soil": "Sandy Loam, Red",        "suitable_ph_min": 5.5, "suitable_ph_max": 7.5,
                "temperature_min": 25, "temperature_max": 38, "rainfall_min": 400, "rainfall_max": 1000,
                "water_requirement": "Low", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 30:15:15 kg/ha",
                "sowing_period": "June - July", "harvesting_period": "September - October",
                "irrigation_method": "Rainfed / 2-3 irrigations", "common_diseases": "Phyllody, Leaf Spot, Powdery Mildew",
                "crop_description": "One of the oldest oilseeds. High sesamin content. Gujarat is leading til producer. Grown in Jamnagar, Rajkot, Surendranagar.",
            },
            {
                "crop_name": "Soybean",                    "crop_name_gujarati": "સોયાબીન",
                "scientific_name": "Glycine max",          "crop_category": "Oilseed",
                "growing_season": "Kharif",                "crop_duration_days": 100,
                "sowing_months": "June - July",            "harvesting_months": "September - October",
                "suitable_soil": "Sandy Loam, Black, Clay Loam", "suitable_ph_min": 6.0, "suitable_ph_max": 7.5,
                "temperature_min": 20, "temperature_max": 32, "rainfall_min": 600, "rainfall_max": 1200,
                "water_requirement": "Medium", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 30:70:40 kg/ha + Rhizobium inoculant",
                "sowing_period": "June 20 - July 15", "harvesting_period": "September - October",
                "irrigation_method": "Drip/Sprinkler - 4-5 irrigations", "common_diseases": "Rust, Purple Seed Stain, Collar Rot",
                "crop_description": "High protein-oil dual-purpose legume. Growing importance in South and Central Gujarat.",
            },
            {
                "crop_name": "Sunflower",                  "crop_name_gujarati": "સૂર્યમુખી",
                "scientific_name": "Helianthus annuus",    "crop_category": "Oilseed",
                "growing_season": "Rabi",                  "crop_duration_days": 95,
                "sowing_months": "October - November",     "harvesting_months": "February - March",
                "suitable_soil": "Sandy Loam, Alluvial",   "suitable_ph_min": 6.0, "suitable_ph_max": 7.5,
                "temperature_min": 15, "temperature_max": 30, "rainfall_min": 400, "rainfall_max": 1000,
                "water_requirement": "Medium", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 90:60:30 kg/ha + Boron 2 kg/ha",
                "sowing_period": "October - November", "harvesting_period": "February - March",
                "irrigation_method": "5-6 irrigations (critical at flowering and seed fill)", "common_diseases": "Alternaria Blight, Powdery Mildew, Stem Rot",
                "crop_description": "High-value rabi oilseed with 40%+ oil content. Grown in Mehsana, Banaskantha, Gandhinagar.",
            },
            # ============ VEGETABLES ============
            {
                "crop_name": "Tomato",                     "crop_name_gujarati": "ટામેટા",
                "scientific_name": "Solanum lycopersicum", "crop_category": "Vegetable",
                "growing_season": "Rabi",                  "crop_duration_days": 120,
                "sowing_months": "September - October",    "harvesting_months": "January - March",
                "suitable_soil": "Sandy Loam, Alluvial",   "suitable_ph_min": 6.0, "suitable_ph_max": 7.0,
                "temperature_min": 15, "temperature_max": 30, "rainfall_min": 600, "rainfall_max": 1200,
                "water_requirement": "High", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 150:75:60 kg/ha + FYM 25 t/ha",
                "sowing_period": "September - October (nursery)", "harvesting_period": "January - March",
                "irrigation_method": "Drip - 7-10 days interval", "common_diseases": "Early Blight, Late Blight, Leaf Curl, TSWV",
                "crop_description": "Major vegetable with high market value. Grown extensively in Vadodara, Surat, Valsad districts.",
            },
            {
                "crop_name": "Potato",                     "crop_name_gujarati": "બટેટા",
                "scientific_name": "Solanum tuberosum",    "crop_category": "Vegetable",
                "growing_season": "Rabi",                  "crop_duration_days": 100,
                "sowing_months": "October - November",     "harvesting_months": "January - February",
                "suitable_soil": "Sandy Loam, Alluvial",   "suitable_ph_min": 5.5, "suitable_ph_max": 6.5,
                "temperature_min": 10, "temperature_max": 22, "rainfall_min": 400, "rainfall_max": 800,
                "water_requirement": "High", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 150:100:80 kg/ha",
                "sowing_period": "October 15 - November 15", "harvesting_period": "January - February",
                "irrigation_method": "Furrow irrigation - 7-10 day intervals", "common_diseases": "Late Blight, Early Blight, Common Scab",
                "crop_description": "Cool-weather tuber crop. Major in Deesa (Banaskantha), Mehsana. Gujarat is top potato producing state.",
            },
            {
                "crop_name": "Onion",                      "crop_name_gujarati": "ડુંગળી",
                "scientific_name": "Allium cepa",          "crop_category": "Vegetable",
                "growing_season": "Rabi",                  "crop_duration_days": 130,
                "sowing_months": "October - November",     "harvesting_months": "February - April",
                "suitable_soil": "Sandy Loam, Alluvial",   "suitable_ph_min": 6.0, "suitable_ph_max": 7.5,
                "temperature_min": 10, "temperature_max": 25, "rainfall_min": 500, "rainfall_max": 900,
                "water_requirement": "Medium", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 100:50:50 kg/ha + Sulphur 20 kg/ha",
                "sowing_period": "October - November (nursery)", "harvesting_period": "February - April",
                "irrigation_method": "Drip/Furrow - 7-8 day interval", "common_diseases": "Purple Blotch, Stemphylium Blight, Downy Mildew",
                "crop_description": "Critical vegetable with strong export market. Grown in Bhavnagar, Surendranagar, Rajkot.",
            },
            {
                "crop_name": "Brinjal (Eggplant)",         "crop_name_gujarati": "રીંગણ",
                "scientific_name": "Solanum melongena",    "crop_category": "Vegetable",
                "growing_season": "Kharif",                "crop_duration_days": 150,
                "sowing_months": "June - July",            "harvesting_months": "September - February",
                "suitable_soil": "Sandy Loam, Alluvial",   "suitable_ph_min": 5.5, "suitable_ph_max": 7.0,
                "temperature_min": 20, "temperature_max": 35, "rainfall_min": 600, "rainfall_max": 1200,
                "water_requirement": "Medium", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 100:60:60 kg/ha",
                "sowing_period": "June - July (nursery)", "harvesting_period": "September - February (continuous)",
                "irrigation_method": "Drip - 5-7 day interval", "common_diseases": "Phomopsis Fruit Rot, Shoot & Fruit Borer, Little Leaf",
                "crop_description": "Year-round vegetable crop. Grown across Gujarat, especially in Surat, Bharuch, Vadodara districts.",
            },
            {
                "crop_name": "Okra (Bhindi/Lady Finger)", "crop_name_gujarati": "ભીંડો",
                "scientific_name": "Abelmoschus esculentus", "crop_category": "Vegetable",
                "growing_season": "Kharif",                "crop_duration_days": 75,
                "sowing_months": "June",                   "harvesting_months": "August - September",
                "suitable_soil": "Sandy Loam, Alluvial",   "suitable_ph_min": 6.0, "suitable_ph_max": 7.5,
                "temperature_min": 22, "temperature_max": 38, "rainfall_min": 500, "rainfall_max": 1200,
                "water_requirement": "Medium", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 100:50:50 kg/ha",
                "sowing_period": "June - July", "harvesting_period": "July - September",
                "irrigation_method": "Drip/Furrow - 5-7 days", "common_diseases": "Yellow Vein Mosaic Virus, Powdery Mildew, Root Knot Nematode",
                "crop_description": "Warm-season vegetable. High demand in domestic market. Grown in Vadodara, Surat, Kheda.",
            },
            {
                "crop_name": "Cauliflower",                "crop_name_gujarati": "ફ્લાવર / કોબી ફ્લાવર",
                "scientific_name": "Brassica oleracea var. botrytis", "crop_category": "Vegetable",
                "growing_season": "Rabi",                  "crop_duration_days": 90,
                "sowing_months": "September - October",    "harvesting_months": "December - February",
                "suitable_soil": "Alluvial, Sandy Loam",   "suitable_ph_min": 6.0, "suitable_ph_max": 7.0,
                "temperature_min": 10, "temperature_max": 22, "rainfall_min": 500, "rainfall_max": 900,
                "water_requirement": "High", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 150:60:60 kg/ha + Boron 2 kg/ha",
                "sowing_period": "September - October (nursery)", "harvesting_period": "December - February",
                "irrigation_method": "Drip/Sprinkler - 7-10 days", "common_diseases": "Black Rot, Downy Mildew, Clubroot",
                "crop_description": "Cool-season Brassica vegetable. High demand in winter. Major production in Kheda, Anand, Vadodara.",
            },
            {
                "crop_name": "Chilli",                     "crop_name_gujarati": "મરચું",
                "scientific_name": "Capsicum annuum",      "crop_category": "Vegetable",
                "growing_season": "Kharif",                "crop_duration_days": 160,
                "sowing_months": "June - July",            "harvesting_months": "October - March",
                "suitable_soil": "Sandy Loam, Clay Loam",  "suitable_ph_min": 6.0, "suitable_ph_max": 7.0,
                "temperature_min": 20, "temperature_max": 30, "rainfall_min": 600, "rainfall_max": 1200,
                "water_requirement": "Medium", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 150:60:60 kg/ha",
                "sowing_period": "June (nursery)", "harvesting_period": "October - February",
                "irrigation_method": "Drip - 6-8 day interval", "common_diseases": "Anthracnose, Die Back, Chilli Mosaic Virus, Thrips",
                "crop_description": "Major spice-vegetable with high export potential. Grown in Kheda, Anand, Vadodara for Jwala and other varieties.",
            },
            {
                "crop_name": "Bottle Gourd",               "crop_name_gujarati": "દૂધી / ઘીયા",
                "scientific_name": "Lagenaria siceraria",  "crop_category": "Vegetable",
                "growing_season": "Zaid",                  "crop_duration_days": 75,
                "sowing_months": "February - March",       "harvesting_months": "April - June",
                "suitable_soil": "Sandy Loam, Alluvial",   "suitable_ph_min": 6.0, "suitable_ph_max": 7.5,
                "temperature_min": 22, "temperature_max": 38, "rainfall_min": 400, "rainfall_max": 900,
                "water_requirement": "High", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 100:60:40 kg/ha + FYM 25 t/ha",
                "sowing_period": "February - March", "harvesting_period": "April - June",
                "irrigation_method": "Drip/Flood - 5 day interval", "common_diseases": "Powdery Mildew, Downy Mildew, Fruit Fly",
                "crop_description": "Popular summer cucurbit vegetable. High water content, used for cooking and juice.",
            },
            {
                "crop_name": "Bitter Gourd",               "crop_name_gujarati": "કારેલા",
                "scientific_name": "Momordica charantia",  "crop_category": "Vegetable",
                "growing_season": "Zaid",                  "crop_duration_days": 90,
                "sowing_months": "February - March",       "harvesting_months": "May - July",
                "suitable_soil": "Sandy Loam, Clay Loam",  "suitable_ph_min": 5.5, "suitable_ph_max": 7.5,
                "temperature_min": 22, "temperature_max": 38, "rainfall_min": 400, "rainfall_max": 1000,
                "water_requirement": "Medium", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 100:60:60 kg/ha",
                "sowing_period": "February - March", "harvesting_period": "April - July",
                "irrigation_method": "Drip/Furrow - 5-7 days", "common_diseases": "Powdery Mildew, Fruit Fly, Root Knot Nematode",
                "crop_description": "Medicinal-vegetable with anti-diabetic properties. High market demand in urban areas.",
            },
            {
                "crop_name": "Carrot",                     "crop_name_gujarati": "ગાજર",
                "scientific_name": "Daucus carota",        "crop_category": "Vegetable",
                "growing_season": "Rabi",                  "crop_duration_days": 100,
                "sowing_months": "October - November",     "harvesting_months": "January - March",
                "suitable_soil": "Sandy Loam, Alluvial",   "suitable_ph_min": 6.0, "suitable_ph_max": 7.0,
                "temperature_min": 7, "temperature_max": 22, "rainfall_min": 400, "rainfall_max": 800,
                "water_requirement": "Medium", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 100:60:60 kg/ha + Boron 2 kg/ha",
                "sowing_period": "October - November", "harvesting_period": "January - March",
                "irrigation_method": "Sprinkler/Furrow - 7-10 days", "common_diseases": "Alternaria Leaf Blight, Cavity Spot, Carrot Fly",
                "crop_description": "Cool-season root vegetable. High beta-carotene content. Grown in North and Central Gujarat.",
            },
            # ============ FRUITS ============
            {
                "crop_name": "Mango (Kesar / Alphonso)",  "crop_name_gujarati": "કેરી (કેસર)",
                "scientific_name": "Mangifera indica",    "crop_category": "Fruit",
                "growing_season": "Perennial",            "crop_duration_days": 365,
                "sowing_months": "July - August (planting)", "harvesting_months": "May - July",
                "suitable_soil": "Sandy Loam, Alluvial",  "suitable_ph_min": 5.5, "suitable_ph_max": 7.5,
                "temperature_min": 20, "temperature_max": 42, "rainfall_min": 750, "rainfall_max": 2500,
                "water_requirement": "Medium", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 1200:600:1200 g/tree/year (Adult tree)",
                "sowing_period": "July - August (planting year 1)", "harvesting_period": "May - July",
                "irrigation_method": "Drip/Flood - Critical for flowering period", "common_diseases": "Anthracnose, Powdery Mildew, Mango Hoppers",
                "crop_description": "King of Fruits. Kesar mango from Gir (Junagadh, Amreli) has GI tag. Largest mango producing district: Junagadh.",
            },
            {
                "crop_name": "Banana",                    "crop_name_gujarati": "કેળાં",
                "scientific_name": "Musa paradisiaca",   "crop_category": "Fruit",
                "growing_season": "Annual",              "crop_duration_days": 365,
                "sowing_months": "February - April",     "harvesting_months": "12-15 months after planting",
                "suitable_soil": "Sandy Loam, Clay Loam, Alluvial", "suitable_ph_min": 6.0, "suitable_ph_max": 7.5,
                "temperature_min": 15, "temperature_max": 38, "rainfall_min": 1000, "rainfall_max": 2000,
                "water_requirement": "High", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 200:60:300 g/plant/cycle",
                "sowing_period": "February - April (Sucker/TC planting)", "harvesting_period": "12-15 months after planting",
                "irrigation_method": "Drip - daily/alternate day for high yield", "common_diseases": "Panama Wilt (Fusarium), Sigatoka, Banana Bunchy Top",
                "crop_description": "Major tropical fruit. Anand, Kheda, Bharuch, Narmada are major banana belts of Gujarat. G9 variety most popular.",
            },
            {
                "crop_name": "Papaya",                    "crop_name_gujarati": "પપૈયા",
                "scientific_name": "Carica papaya",      "crop_category": "Fruit",
                "growing_season": "Annual",              "crop_duration_days": 300,
                "sowing_months": "June - July",          "harvesting_months": "9-12 months after planting",
                "suitable_soil": "Sandy Loam, Alluvial", "suitable_ph_min": 6.0, "suitable_ph_max": 7.0,
                "temperature_min": 20, "temperature_max": 38, "rainfall_min": 1000, "rainfall_max": 2000,
                "water_requirement": "Medium", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 100:50:100 g/plant/month",
                "sowing_period": "June - July", "harvesting_period": "9-12 months after planting",
                "irrigation_method": "Drip - 3-5 day interval", "common_diseases": "Papaya Ring Spot Virus, Anthracnose, Powdery Mildew",
                "crop_description": "Fast-growing tropical fruit. High demand for raw (vegetable papaya) and ripe fruit. Rich in Vitamins A, C.",
            },
            {
                "crop_name": "Pomegranate",               "crop_name_gujarati": "દાડમ",
                "scientific_name": "Punica granatum",    "crop_category": "Fruit",
                "growing_season": "Perennial",           "crop_duration_days": 365,
                "sowing_months": "July - August",        "harvesting_months": "September - December",
                "suitable_soil": "Sandy Loam, Red",      "suitable_ph_min": 5.5, "suitable_ph_max": 8.0,
                "temperature_min": 10, "temperature_max": 45, "rainfall_min": 500, "rainfall_max": 1000,
                "water_requirement": "Low", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 600:200:200 g/tree/year",
                "sowing_period": "July - August (cutting/planting)", "harvesting_period": "September - December (Mrig bahar)",
                "irrigation_method": "Drip - 3-5 day interval", "common_diseases": "Bacterial Blight (Oily Spot), Fruit Borer, Cercospora",
                "crop_description": "Super fruit with high export demand. Drought tolerant. Grown in Bhavnagar, Surendranagar, Rajkot.",
            },
            {
                "crop_name": "Guava",                    "crop_name_gujarati": "જામફળ",
                "scientific_name": "Psidium guajava",   "crop_category": "Fruit",
                "growing_season": "Perennial",          "crop_duration_days": 365,
                "sowing_months": "July - August",       "harvesting_months": "October - January",
                "suitable_soil": "Sandy Loam, Alluvial, Black", "suitable_ph_min": 5.0, "suitable_ph_max": 8.0,
                "temperature_min": 10, "temperature_max": 42, "rainfall_min": 600, "rainfall_max": 1500,
                "water_requirement": "Low", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 600:400:600 g/tree/year",
                "sowing_period": "July - August", "harvesting_period": "October - January",
                "irrigation_method": "Drip/Flood - 10-15 day interval", "common_diseases": "Wilt, Fruit Fly, Rust",
                "crop_description": "Hardy tropical fruit with high Vitamin C. Low input crop. Grown across Gujarat for local and export markets.",
            },
            {
                "crop_name": "Sapota (Chikoo)",          "crop_name_gujarati": "ચીકુ",
                "scientific_name": "Manilkara zapota",  "crop_category": "Fruit",
                "growing_season": "Perennial",          "crop_duration_days": 365,
                "sowing_months": "July - August",       "harvesting_months": "October - February",
                "suitable_soil": "Sandy Loam, Alluvial", "suitable_ph_min": 6.0, "suitable_ph_max": 8.0,
                "temperature_min": 15, "temperature_max": 42, "rainfall_min": 1000, "rainfall_max": 2000,
                "water_requirement": "Medium", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 600:200:600 g/tree/year",
                "sowing_period": "July - August", "harvesting_period": "October - February",
                "irrigation_method": "Drip/Flood - 10 day interval", "common_diseases": "Leaf Spot, Scale Insects, Anthracnose",
                "crop_description": "Major commercial fruit. Valsad and Navsari are top chikoo producing districts in India. High export demand.",
            },
            {
                "crop_name": "Lemon",                    "crop_name_gujarati": "લીંબુ",
                "scientific_name": "Citrus limon",      "crop_category": "Fruit",
                "growing_season": "Perennial",          "crop_duration_days": 365,
                "sowing_months": "June - July",         "harvesting_months": "Year-round (peak Jan-March)",
                "suitable_soil": "Sandy Loam, Alluvial", "suitable_ph_min": 6.0, "suitable_ph_max": 7.5,
                "temperature_min": 15, "temperature_max": 40, "rainfall_min": 750, "rainfall_max": 1200,
                "water_requirement": "Medium", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 600:300:600 g/tree/year",
                "sowing_period": "June - July", "harvesting_period": "Year-round",
                "irrigation_method": "Drip - 7-10 day interval", "common_diseases": "Citrus Canker, Tristeza Virus, Phytophthora Gummosis",
                "crop_description": "Popular citrus for juice and culinary use. High demand throughout the year. Grown across Gujarat.",
            },
            {
                "crop_name": "Watermelon",               "crop_name_gujarati": "તડબૂચ",
                "scientific_name": "Citrullus lanatus", "crop_category": "Fruit",
                "growing_season": "Zaid",               "crop_duration_days": 85,
                "sowing_months": "February - March",    "harvesting_months": "May - June",
                "suitable_soil": "Sandy Loam, Sandy",   "suitable_ph_min": 6.0, "suitable_ph_max": 7.5,
                "temperature_min": 22, "temperature_max": 42, "rainfall_min": 400, "rainfall_max": 1000,
                "water_requirement": "High", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 100:60:60 kg/ha",
                "sowing_period": "February - March", "harvesting_period": "May - June",
                "irrigation_method": "Drip/Flood - 5-7 day interval", "common_diseases": "Powdery Mildew, Fusarium Wilt, Fruit Fly",
                "crop_description": "Major summer fruit crop. High demand in Gujarat summer. Grown along river beds in Vadodara, Bharuch, Narmada.",
            },
            # ============ SPICES ============
            {
                "crop_name": "Cumin (Jeera)",            "crop_name_gujarati": "જીરું",
                "scientific_name": "Cuminum cyminum",   "crop_category": "Spice",
                "growing_season": "Rabi",               "crop_duration_days": 100,
                "sowing_months": "October - November",  "harvesting_months": "February - March",
                "suitable_soil": "Sandy Loam, Sandy",   "suitable_ph_min": 7.0, "suitable_ph_max": 8.0,
                "temperature_min": 7, "temperature_max": 25, "rainfall_min": 200, "rainfall_max": 500,
                "water_requirement": "Low", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 30:15:15 kg/ha + Sulphur 10 kg/ha",
                "sowing_period": "October 20 - November 20", "harvesting_period": "February - March",
                "irrigation_method": "Sprinkler - 2-3 light irrigations (critical at flowering)", "common_diseases": "Blight (Alternaria), Powdery Mildew, Aphids",
                "crop_description": "India's #1 cumin exporting state. Patan, Banaskantha, Mehsana, Rajkot are major cumin belts. APMC Unjha is world's largest cumin market.",
            },
            {
                "crop_name": "Fennel (Variyali)",        "crop_name_gujarati": "વરિયાળી",
                "scientific_name": "Foeniculum vulgare", "crop_category": "Spice",
                "growing_season": "Rabi",               "crop_duration_days": 160,
                "sowing_months": "October - November",  "harvesting_months": "March - April",
                "suitable_soil": "Sandy Loam, Alluvial", "suitable_ph_min": 6.5, "suitable_ph_max": 7.5,
                "temperature_min": 7, "temperature_max": 25, "rainfall_min": 400, "rainfall_max": 800,
                "water_requirement": "Low", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 60:30:30 kg/ha",
                "sowing_period": "October - November", "harvesting_period": "March - April",
                "irrigation_method": "Sprinkler - 4-5 irrigations", "common_diseases": "Powdery Mildew, Ramularia Blight, Aphids",
                "crop_description": "Major export spice. Gujarat produces 90%+ of India's fennel. Patan district is the fennel capital. APMC Unjha handles majority of trade.",
            },
            {
                "crop_name": "Coriander",                "crop_name_gujarati": "ધાણા",
                "scientific_name": "Coriandrum sativum", "crop_category": "Spice",
                "growing_season": "Rabi",               "crop_duration_days": 100,
                "sowing_months": "October - November",  "harvesting_months": "February - March",
                "suitable_soil": "Sandy Loam, Alluvial", "suitable_ph_min": 6.5, "suitable_ph_max": 7.5,
                "temperature_min": 10, "temperature_max": 28, "rainfall_min": 300, "rainfall_max": 700,
                "water_requirement": "Low", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 30:15:15 kg/ha",
                "sowing_period": "October - November", "harvesting_period": "February - March",
                "irrigation_method": "2-3 irrigations", "common_diseases": "Stem Gall, Powdery Mildew, Aphids",
                "crop_description": "Essential culinary spice. Used as fresh herb and dried seed. Grown in Banaskantha, Patan, Surendranagar.",
            },
            {
                "crop_name": "Fenugreek (Methi)",        "crop_name_gujarati": "મેથી",
                "scientific_name": "Trigonella foenum-graecum", "crop_category": "Spice",
                "growing_season": "Rabi",               "crop_duration_days": 90,
                "sowing_months": "October - November",  "harvesting_months": "January - February",
                "suitable_soil": "Sandy Loam, Alluvial", "suitable_ph_min": 6.0, "suitable_ph_max": 7.5,
                "temperature_min": 10, "temperature_max": 28, "rainfall_min": 400, "rainfall_max": 800,
                "water_requirement": "Low", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 20:40:20 kg/ha",
                "sowing_period": "October - November", "harvesting_period": "January - February",
                "irrigation_method": "2-3 irrigations", "common_diseases": "Powdery Mildew, Root Rot, Aphids",
                "crop_description": "Multipurpose spice-vegetable. Leaves used as vegetable, seeds as spice. Nutritional and medicinal value.",
            },
            {
                "crop_name": "Ajwain (Carom Seeds)",    "crop_name_gujarati": "અજમો",
                "scientific_name": "Trachyspermum ammi", "crop_category": "Spice",
                "growing_season": "Rabi",               "crop_duration_days": 120,
                "sowing_months": "October",             "harvesting_months": "February - March",
                "suitable_soil": "Sandy Loam",          "suitable_ph_min": 6.0, "suitable_ph_max": 7.5,
                "temperature_min": 10, "temperature_max": 28, "rainfall_min": 400, "rainfall_max": 800,
                "water_requirement": "Low", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 30:20:20 kg/ha",
                "sowing_period": "October - November", "harvesting_period": "February - March",
                "irrigation_method": "2-3 light irrigations", "common_diseases": "Powdery Mildew, Aphids, Seed Rot",
                "crop_description": "Pungent aromatic spice with medicinal value. Used in traditional cuisine. Gujarat is major producer.",
            },
            {
                "crop_name": "Garlic",                  "crop_name_gujarati": "લસણ",
                "scientific_name": "Allium sativum",   "crop_category": "Spice",
                "growing_season": "Rabi",              "crop_duration_days": 160,
                "sowing_months": "October - November", "harvesting_months": "March - April",
                "suitable_soil": "Sandy Loam, Alluvial", "suitable_ph_min": 6.0, "suitable_ph_max": 7.5,
                "temperature_min": 7, "temperature_max": 22, "rainfall_min": 500, "rainfall_max": 900,
                "water_requirement": "Medium", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 100:50:50 kg/ha + Sulphur 20 kg/ha",
                "sowing_period": "October - November", "harvesting_period": "March - April",
                "irrigation_method": "Furrow/Drip - 7-10 days", "common_diseases": "Purple Blotch, Stemphylium Blight, Basal Rot",
                "crop_description": "Major spice with medicinal properties. Bhavnagar, Surendranagar, Rajkot are garlic growing districts.",
            },
            # ============ CASH CROPS ============
            {
                "crop_name": "Cotton (Kapas)",          "crop_name_gujarati": "કપાસ",
                "scientific_name": "Gossypium hirsutum", "crop_category": "Cash Crop",
                "growing_season": "Kharif",             "crop_duration_days": 180,
                "sowing_months": "May - June",          "harvesting_months": "October - January",
                "suitable_soil": "Black, Clay Loam",   "suitable_ph_min": 6.0, "suitable_ph_max": 7.5,
                "temperature_min": 20, "temperature_max": 42, "rainfall_min": 500, "rainfall_max": 1200,
                "water_requirement": "Medium", "sunlight_requirement": "Full Sun (10+ hours)",
                "fertilizer_requirement": "N:P:K - 150:60:60 kg/ha for Bt Cotton",
                "sowing_period": "May 20 - June 30", "harvesting_period": "October - January (3-4 pickings)",
                "irrigation_method": "Drip - critical at flowering and boll development", "common_diseases": "Bollworm (Pink, American), Whitfly, Cotton Leaf Curl Virus, Root Rot",
                "crop_description": "King cash crop of Gujarat. India's #1 cotton producing state. Saurashtra is cotton belt - Surendranagar, Rajkot, Bhavnagar lead production. BG-II Bt Cotton most common.",
            },
            {
                "crop_name": "Sugarcane",               "crop_name_gujarati": "શેરડી",
                "scientific_name": "Saccharum officinarum", "crop_category": "Cash Crop",
                "growing_season": "Annual",             "crop_duration_days": 365,
                "sowing_months": "February - March",   "harvesting_months": "December - March (next year)",
                "suitable_soil": "Alluvial, Black, Sandy Loam", "suitable_ph_min": 6.0, "suitable_ph_max": 7.5,
                "temperature_min": 20, "temperature_max": 42, "rainfall_min": 1000, "rainfall_max": 2500,
                "water_requirement": "High", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 250:100:100 kg/ha + FYM 20 t/ha",
                "sowing_period": "February - March (planting)", "harvesting_period": "December - March (10-12 months)",
                "irrigation_method": "Drip - 7 day interval or flood irrigation", "common_diseases": "Red Rot, Smut, Wilt, Top Shoot Borer",
                "crop_description": "Major industrial cash crop. Sugar mills concentrated in Anand, Kheda, Vadodara, Bharuch and Surat districts. South Gujarat sugarcane belt.",
            },
            {
                "crop_name": "Tobacco",                 "crop_name_gujarati": "તમાકુ",
                "scientific_name": "Nicotiana tabacum", "crop_category": "Cash Crop",
                "growing_season": "Rabi",               "crop_duration_days": 120,
                "sowing_months": "October - November",  "harvesting_months": "February - March",
                "suitable_soil": "Sandy Loam, Red",    "suitable_ph_min": 5.5, "suitable_ph_max": 7.5,
                "temperature_min": 15, "temperature_max": 35, "rainfall_min": 500, "rainfall_max": 1000,
                "water_requirement": "Medium", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 90:60:60 kg/ha (Flue-cured variety)",
                "sowing_period": "October - November", "harvesting_period": "February - March",
                "irrigation_method": "Flood/Furrow - 4-5 irrigations", "common_diseases": "Mosaic Virus, Frog Eye, Root Knot Nematode",
                "crop_description": "Major commercial crop. Anand, Kheda districts are tobacco growing regions. Bidi tobacco major variety.",
            },
            # ============ FODDER ============
            {
                "crop_name": "Lucerne (Rijka)",          "crop_name_gujarati": "રિજકો / લ્યૂઝર્ન",
                "scientific_name": "Medicago sativa",   "crop_category": "Fodder",
                "growing_season": "Rabi",               "crop_duration_days": 210,
                "sowing_months": "October - November",  "harvesting_months": "December - May (multiple cuts)",
                "suitable_soil": "Sandy Loam, Alluvial", "suitable_ph_min": 6.5, "suitable_ph_max": 8.0,
                "temperature_min": 7, "temperature_max": 28, "rainfall_min": 400, "rainfall_max": 1000,
                "water_requirement": "High", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 25:80:40 kg/ha + Rhizobium inoculant",
                "sowing_period": "October - November", "harvesting_period": "December - May (5-7 cuts)",
                "irrigation_method": "Flood - 7-10 day interval for maximum yield", "common_diseases": "Stem Rot, Phytophthora Root Rot, Downy Mildew",
                "crop_description": "Perennial fodder legume with 20-25% crude protein. High livestock demand. Grown in North Gujarat, Anand, Kheda.",
            },
            {
                "crop_name": "Berseem",                  "crop_name_gujarati": "બરસીમ",
                "scientific_name": "Trifolium alexandrinum", "crop_category": "Fodder",
                "growing_season": "Rabi",               "crop_duration_days": 160,
                "sowing_months": "October - November",  "harvesting_months": "December - April",
                "suitable_soil": "Clay Loam, Alluvial", "suitable_ph_min": 6.5, "suitable_ph_max": 8.0,
                "temperature_min": 10, "temperature_max": 28, "rainfall_min": 500, "rainfall_max": 1000,
                "water_requirement": "High", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 25:80:40 kg/ha",
                "sowing_period": "October - November", "harvesting_period": "December - April (4-6 cuts)",
                "irrigation_method": "Flood - 7-10 day intervals", "common_diseases": "Stem Rot, Root Rot, Aphids",
                "crop_description": "High-quality legume fodder. 15-18% crude protein. Major fodder crop of North Gujarat for dairy animals.",
            },
            {
                "crop_name": "Fodder Sorghum",           "crop_name_gujarati": "ઘાસ જુવાર",
                "scientific_name": "Sorghum bicolor (fodder var.)", "crop_category": "Fodder",
                "growing_season": "Kharif",             "crop_duration_days": 75,
                "sowing_months": "June - July",         "harvesting_months": "August - September",
                "suitable_soil": "Black, Sandy Loam",   "suitable_ph_min": 6.0, "suitable_ph_max": 7.5,
                "temperature_min": 20, "temperature_max": 40, "rainfall_min": 400, "rainfall_max": 1000,
                "water_requirement": "Low", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 100:40:40 kg/ha",
                "sowing_period": "June - July", "harvesting_period": "August - September (2 cuts)",
                "irrigation_method": "2-3 irrigations", "common_diseases": "Ergot, Head Smut, Shoot Fly",
                "crop_description": "Quick-growing kharif fodder crop. Drought-tolerant. Major livestock feed across Gujarat.",
            },
            {
                "crop_name": "Napier Grass (Elephant Grass)", "crop_name_gujarati": "નેપિયર ઘાસ",
                "scientific_name": "Pennisetum purpureum", "crop_category": "Fodder",
                "growing_season": "Perennial",          "crop_duration_days": 365,
                "sowing_months": "June - July",         "harvesting_months": "Year-round (every 45-60 days)",
                "suitable_soil": "Sandy Loam, Alluvial, Black", "suitable_ph_min": 5.5, "suitable_ph_max": 7.5,
                "temperature_min": 20, "temperature_max": 42, "rainfall_min": 700, "rainfall_max": 2000,
                "water_requirement": "Medium", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 200:80:60 kg/ha/year",
                "sowing_period": "June - July (stem cuttings)", "harvesting_period": "Every 45-60 days (10-12 cuts/year)",
                "irrigation_method": "Drip/Flood - 15-20 day intervals", "common_diseases": "Rust, Smut, Head Caterpillar",
                "crop_description": "Perennial high-yielding fodder grass. Used for stall-feeding dairy cattle. 60-80 tonnes green matter/ha/year.",
            },
            # ============ MEDICINAL ============
            {
                "crop_name": "Isabgol (Psyllium)",      "crop_name_gujarati": "ઈસબગોલ",
                "scientific_name": "Plantago ovata",   "crop_category": "Medicinal",
                "growing_season": "Rabi",              "crop_duration_days": 110,
                "sowing_months": "November",           "harvesting_months": "February - March",
                "suitable_soil": "Sandy Loam, Sandy",  "suitable_ph_min": 7.0, "suitable_ph_max": 8.0,
                "temperature_min": 7, "temperature_max": 25, "rainfall_min": 300, "rainfall_max": 600,
                "water_requirement": "Low", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "N:P:K - 50:30:30 kg/ha (avoid excess N)",
                "sowing_period": "November (after October rains)", "harvesting_period": "February - March",
                "irrigation_method": "Sprinkler - 2-3 light irrigations (flooding harmful)", "common_diseases": "Downy Mildew, Root Rot (avoid waterlogging)",
                "crop_description": "India contributes 85% of global isabgol production. Gujarat (Banaskantha, Patan) and Rajasthan are major producers. Used as laxative and in food industry.",
            },
            {
                "crop_name": "Aloe Vera",               "crop_name_gujarati": "કૂંવારપાઠ / ઘ્ય-કુમારી",
                "scientific_name": "Aloe barbadensis",  "crop_category": "Medicinal",
                "growing_season": "Perennial",          "crop_duration_days": 365,
                "sowing_months": "July - August",       "harvesting_months": "12-18 months (then every 3 months)",
                "suitable_soil": "Sandy Loam, Red",    "suitable_ph_min": 6.0, "suitable_ph_max": 7.5,
                "temperature_min": 10, "temperature_max": 42, "rainfall_min": 400, "rainfall_max": 1000,
                "water_requirement": "Low", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "FYM 10 t/ha + N:P:K - 50:30:30 kg/ha",
                "sowing_period": "July - August (suckers)", "harvesting_period": "Year-round after establishment",
                "irrigation_method": "Drip - 15-20 day interval (drought tolerant)", "common_diseases": "Basal Rot, Anthracnose, Root Rot (overwatering)",
                "crop_description": "High-value medicinal crop. FMCG and pharmaceutical demand. Kutch, Banaskantha, Surendranagar growing districts.",
            },
            {
                "crop_name": "Ashwagandha",             "crop_name_gujarati": "અશ્વગંધા",
                "scientific_name": "Withania somnifera", "crop_category": "Medicinal",
                "growing_season": "Kharif",             "crop_duration_days": 160,
                "sowing_months": "July - August",       "harvesting_months": "December - January",
                "suitable_soil": "Sandy Loam, Red",    "suitable_ph_min": 7.5, "suitable_ph_max": 8.0,
                "temperature_min": 20, "temperature_max": 38, "rainfall_min": 500, "rainfall_max": 750,
                "water_requirement": "Low", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "FYM 10 t/ha + N:P:K - 15:15:15 kg/ha",
                "sowing_period": "July - August", "harvesting_period": "December - January (roots harvested)",
                "irrigation_method": "Rainfed / 2-3 protective irrigations", "common_diseases": "Seedling Rot (Alternaria), Root Rot",
                "crop_description": "Adaptogenic medicinal herb with Ayurvedic importance. High market demand from pharmaceutical industry. Growing cultivation in Gujarat.",
            },
            {
                "crop_name": "Tulsi (Holy Basil)",      "crop_name_gujarati": "તુલસી",
                "scientific_name": "Ocimum tenuiflorum", "crop_category": "Medicinal",
                "growing_season": "Kharif",             "crop_duration_days": 120,
                "sowing_months": "June - July",         "harvesting_months": "September - November",
                "suitable_soil": "Sandy Loam, Alluvial", "suitable_ph_min": 6.0, "suitable_ph_max": 7.5,
                "temperature_min": 20, "temperature_max": 38, "rainfall_min": 600, "rainfall_max": 1200,
                "water_requirement": "Low", "sunlight_requirement": "Full Sun",
                "fertilizer_requirement": "FYM 15 t/ha + N:P:K - 30:20:20 kg/ha",
                "sowing_period": "June - July", "harvesting_period": "September - November (leaves, seeds)",
                "irrigation_method": "Drip/Sprinkler - 7-10 days", "common_diseases": "Root Rot, Powdery Mildew, Leaf Spot",
                "crop_description": "Sacred and medicinal herb. Oil extracted for pharmaceutical and cosmetic use. Growing demand from herbal companies.",
            },
        ]

        created_count = 0
        updated_count = 0

        for c_data in CROPS:
            cat_code = c_data.get("crop_category")
            cat_obj = CropCategory.objects.filter(category_code=cat_code).first()

            # Map Horticulture (old) to Fruit
            if cat_code == "Horticulture":
                cat_obj = CropCategory.objects.filter(category_code="Fruit").first()
                c_data["crop_category"] = "Fruit"

            defaults = {
                "crop_name_gujarati": c_data.get("crop_name_gujarati", ""),
                "scientific_name": c_data.get("scientific_name", ""),
                "crop_category": c_data["crop_category"],
                "category": cat_obj,
                "crop_description": c_data.get("crop_description", ""),
                "growing_season": c_data.get("growing_season", "Kharif"),
                "crop_duration_days": c_data.get("crop_duration_days", 120),
                "sowing_months": c_data.get("sowing_months", ""),
                "harvesting_months": c_data.get("harvesting_months", ""),
                "suitable_soil": c_data.get("suitable_soil", ""),
                "suitable_ph_min": c_data.get("suitable_ph_min", 6.0),
                "suitable_ph_max": c_data.get("suitable_ph_max", 7.5),
                "temperature_min": c_data.get("temperature_min", 15.0),
                "temperature_max": c_data.get("temperature_max", 35.0),
                "rainfall_min": c_data.get("rainfall_min", 400.0),
                "rainfall_max": c_data.get("rainfall_max", 1200.0),
                "water_requirement": c_data.get("water_requirement", "Medium"),
                "sunlight_requirement": c_data.get("sunlight_requirement", "Full Sun"),
                "fertilizer_requirement": c_data.get("fertilizer_requirement", ""),
                "sowing_period": c_data.get("sowing_period", ""),
                "harvesting_period": c_data.get("harvesting_period", ""),
                "irrigation_method": c_data.get("irrigation_method", ""),
                "common_diseases": c_data.get("common_diseases", ""),
                "data_source": SRC,
                "data_type": "Scientific",
                "reference_date": REF,
                "is_active": True,
            }

            obj, created = Crop.objects.get_or_create(
                crop_name=c_data["crop_name"],
                defaults=defaults
            )

            if created:
                created_count += 1
            else:
                # Update incomplete records
                update_fields = []
                if not obj.crop_name_gujarati and c_data.get("crop_name_gujarati"):
                    obj.crop_name_gujarati = c_data["crop_name_gujarati"]
                    update_fields.append("crop_name_gujarati")
                if not obj.scientific_name and c_data.get("scientific_name"):
                    obj.scientific_name = c_data["scientific_name"]
                    update_fields.append("scientific_name")
                if not obj.crop_description and c_data.get("crop_description"):
                    obj.crop_description = c_data["crop_description"]
                    update_fields.append("crop_description")
                if not obj.category and cat_obj:
                    obj.category = cat_obj
                    update_fields.append("category")
                if not obj.suitable_ph_min:
                    obj.suitable_ph_min = c_data.get("suitable_ph_min", 6.0)
                    update_fields.append("suitable_ph_min")
                if not obj.suitable_ph_max:
                    obj.suitable_ph_max = c_data.get("suitable_ph_max", 7.5)
                    update_fields.append("suitable_ph_max")
                if not obj.rainfall_min:
                    obj.rainfall_min = c_data.get("rainfall_min", 400)
                    update_fields.append("rainfall_min")
                if not obj.rainfall_max:
                    obj.rainfall_max = c_data.get("rainfall_max", 1200)
                    update_fields.append("rainfall_max")
                if update_fields:
                    obj.save(update_fields=update_fields)
                    updated_count += 1

        self.stdout.write(f"  Crops: {created_count} created, {updated_count} updated. Total: {Crop.objects.count()}")

        # --- STEP 3: Seed CropSeasonCalendars for Gujarat Districts ---
        self.stdout.write("Seeding CropSeasonCalendars...")

        # Key district groups for suitability and calendars
        DISTRICT_ZONE = {
            "North Gujarat": ["Banaskantha", "Patan", "Mehsana", "Gandhinagar", "Sabarkantha", "Aravalli"],
            "South Gujarat": ["Surat", "Navsari", "Valsad", "Dang", "Tapi"],
            "Saurashtra": ["Rajkot", "Junagadh", "Jamnagar", "Porbandar", "Amreli", "Bhavnagar", "Morbi", "Devbhumi Dwarka", "Gir Somnath", "Botad"],
            "Central Gujarat": ["Vadodara", "Anand", "Kheda", "Panchmahal", "Dahod", "Mahisagar"],
            "Kutch": ["Kutch"],
            "East Gujarat": ["Narmada", "Bharuch", "Chhota Udaipur"],
        }

        # Representative calendars per crop and zone
        SEASON_CALENDARS = [
            # Kharif - Major crops
            {"crop_name": "Groundnut",     "zone": "Saurashtra",     "season": "Kharif", "sow_s": "June",    "sow_e": "July",      "har_s": "October",  "har_e": "November", "dur": 120, "irr": "Drip - 4-5 irrigations"},
            {"crop_name": "Groundnut",     "zone": "North Gujarat",   "season": "Kharif", "sow_s": "June",    "sow_e": "July",      "har_s": "October",  "har_e": "November", "dur": 120, "irr": "Drip/Sprinkler - 5 irrigations"},
            {"crop_name": "Cotton (Kapas)","zone": "Saurashtra",      "season": "Kharif", "sow_s": "May",     "sow_e": "June",      "har_s": "October",  "har_e": "January",  "dur": 180, "irr": "Drip - critical at flowering"},
            {"crop_name": "Cotton (Kapas)","zone": "Central Gujarat",  "season": "Kharif", "sow_s": "May",     "sow_e": "June",      "har_s": "October",  "har_e": "January",  "dur": 180, "irr": "Drip - 6-8 irrigations"},
            {"crop_name": "Castor",        "zone": "North Gujarat",   "season": "Kharif", "sow_s": "June",    "sow_e": "July",      "har_s": "December", "har_e": "February", "dur": 180, "irr": "Drip - 5-6 irrigations"},
            {"crop_name": "Bajra (Pearl Millet)", "zone": "Saurashtra", "season": "Kharif", "sow_s": "June", "sow_e": "July",      "har_s": "September","har_e": "October",  "dur": 75,  "irr": "Rainfed / 2-3 irrigations"},
            {"crop_name": "Paddy (Rice)",  "zone": "South Gujarat",   "season": "Kharif", "sow_s": "June",    "sow_e": "July",      "har_s": "October",  "har_e": "November", "dur": 130, "irr": "Flooded - 3-5cm standing water"},
            {"crop_name": "Sesame (Til)",  "zone": "Saurashtra",     "season": "Kharif", "sow_s": "June",    "sow_e": "July",      "har_s": "September","har_e": "October",  "dur": 85,  "irr": "Rainfed / 2-3 irrigations"},
            {"crop_name": "Pigeon Pea (Tur/Arhar)", "zone": "Central Gujarat", "season": "Kharif", "sow_s": "June", "sow_e": "July", "har_s": "December", "har_e": "January", "dur": 160, "irr": "2-3 irrigations"},
            {"crop_name": "Green Gram (Moong)", "zone": "Central Gujarat", "season": "Kharif", "sow_s": "June", "sow_e": "July", "har_s": "August",   "har_e": "September","dur": 65,  "irr": "2-3 irrigations"},
            {"crop_name": "Maize",         "zone": "East Gujarat",    "season": "Kharif", "sow_s": "June",    "sow_e": "July",      "har_s": "September","har_e": "October",  "dur": 100, "irr": "5-6 irrigations"},
            # Rabi - Major crops
            {"crop_name": "Wheat",         "zone": "North Gujarat",   "season": "Rabi",   "sow_s": "November","sow_e": "December",  "har_s": "March",    "har_e": "April",    "dur": 120, "irr": "5-6 irrigations"},
            {"crop_name": "Cumin (Jeera)", "zone": "North Gujarat",   "season": "Rabi",   "sow_s": "October", "sow_e": "November",  "har_s": "February", "har_e": "March",    "dur": 100, "irr": "Sprinkler - 2-3 light irrigations"},
            {"crop_name": "Fennel (Variyali)", "zone": "North Gujarat", "season": "Rabi", "sow_s": "October", "sow_e": "November",  "har_s": "March",    "har_e": "April",    "dur": 160, "irr": "5-6 irrigations"},
            {"crop_name": "Mustard",       "zone": "North Gujarat",   "season": "Rabi",   "sow_s": "October", "sow_e": "November",  "har_s": "February", "har_e": "March",    "dur": 110, "irr": "3-4 irrigations"},
            {"crop_name": "Chickpea (Gram)", "zone": "North Gujarat", "season": "Rabi",   "sow_s": "October", "sow_e": "November",  "har_s": "February", "har_e": "March",    "dur": 110, "irr": "Rainfed / 1-2 protective"},
            {"crop_name": "Isabgol (Psyllium)", "zone": "North Gujarat", "season": "Rabi","sow_s": "November","sow_e": "November",  "har_s": "February", "har_e": "March",    "dur": 110, "irr": "Sprinkler - 2-3 light"},
            {"crop_name": "Potato",        "zone": "North Gujarat",   "season": "Rabi",   "sow_s": "October", "sow_e": "November",  "har_s": "January",  "har_e": "February", "dur": 100, "irr": "7-10 day intervals"},
            {"crop_name": "Onion",         "zone": "Saurashtra",     "season": "Rabi",   "sow_s": "October", "sow_e": "November",  "har_s": "February", "har_e": "April",    "dur": 130, "irr": "7-8 day interval"},
            {"crop_name": "Tomato",        "zone": "Central Gujarat", "season": "Rabi",   "sow_s": "September","sow_e": "October",  "har_s": "January",  "har_e": "March",    "dur": 120, "irr": "Drip - 7-10 day interval"},
            {"crop_name": "Lucerne (Rijka)","zone": "North Gujarat",  "season": "Rabi",   "sow_s": "October", "sow_e": "November",  "har_s": "December", "har_e": "May",      "dur": 210, "irr": "7-10 day interval"},
            # Zaid - Summer crops
            {"crop_name": "Watermelon",    "zone": "Central Gujarat", "season": "Zaid",   "sow_s": "February","sow_e": "March",     "har_s": "May",      "har_e": "June",     "dur": 85,  "irr": "5-7 day interval"},
            {"crop_name": "Bottle Gourd",  "zone": "Central Gujarat", "season": "Zaid",   "sow_s": "February","sow_e": "March",     "har_s": "April",    "har_e": "June",     "dur": 75,  "irr": "5 day interval"},
            {"crop_name": "Bitter Gourd",  "zone": "Central Gujarat", "season": "Zaid",   "sow_s": "February","sow_e": "March",     "har_s": "May",      "har_e": "July",     "dur": 90,  "irr": "5-7 days"},
            {"crop_name": "Green Gram (Moong)", "zone": "Central Gujarat", "season": "Zaid","sow_s": "February","sow_e": "March",   "har_s": "May",      "har_e": "June",     "dur": 60,  "irr": "3-4 irrigations"},
            # Perennial
            {"crop_name": "Mango (Kesar / Alphonso)", "zone": "Saurashtra", "season": "Perennial", "sow_s": "July", "sow_e": "August", "har_s": "May", "har_e": "July", "dur": 365, "irr": "Drip - Critical for flowering"},
            {"crop_name": "Banana",        "zone": "Central Gujarat", "season": "Perennial","sow_s": "February","sow_e": "April",    "har_s": "April",    "har_e": "June",     "dur": 365, "irr": "Drip - daily/alternate day"},
            {"crop_name": "Sapota (Chikoo)","zone": "South Gujarat",  "season": "Perennial","sow_s": "July",    "sow_e": "August",   "har_s": "October",  "har_e": "February", "dur": 365, "irr": "Drip - 10 day interval"},
            {"crop_name": "Pomegranate",   "zone": "Saurashtra",     "season": "Perennial","sow_s": "July",    "sow_e": "August",   "har_s": "September","har_e": "December", "dur": 365, "irr": "Drip - 3-5 day interval"},
        ]

        from locations.models import District

        cal_created = 0
        for cal in SEASON_CALENDARS:
            crop_obj = Crop.objects.filter(crop_name=cal["crop_name"]).first()
            if not crop_obj:
                continue

            zone_districts = DISTRICT_ZONE.get(cal["zone"], [])
            for dist_name in zone_districts:
                obj, created = CropSeasonCalendar.objects.get_or_create(
                    crop=crop_obj,
                    state="Gujarat",
                    district=dist_name,
                    season=cal["season"],
                    defaults={
                        "sowing_start_month": cal["sow_s"],
                        "sowing_end_month": cal["sow_e"],
                        "harvest_start_month": cal["har_s"],
                        "harvest_end_month": cal["har_e"],
                        "crop_duration_days": cal["dur"],
                        "irrigation_requirement": cal["irr"],
                        "data_source": SRC,
                        "data_type": "Official University Calendar",
                    }
                )
                if created:
                    cal_created += 1

        self.stdout.write(f"  CropSeasonCalendars: {cal_created} created. Total: {CropSeasonCalendar.objects.count()}")

        # --- STEP 4: Seed CropLocationSuitability ---
        self.stdout.write("Seeding CropLocationSuitability...")

        SUITABILITIES = [
            # Groundnut - Major Saurashtra districts
            {"crop_name": "Groundnut", "district": "Junagadh",    "suitability": "Highly Suitable",     "score": 95, "seasons": "Kharif", "soil": "Sandy Loam, Red",   "advisory": "Preferred variety: GG-20, TG-37A"},
            {"crop_name": "Groundnut", "district": "Rajkot",      "suitability": "Highly Suitable",     "score": 92, "seasons": "Kharif", "soil": "Sandy Loam",        "advisory": "Irrigated groundnut highly profitable"},
            {"crop_name": "Groundnut", "district": "Amreli",      "suitability": "Highly Suitable",     "score": 90, "seasons": "Kharif", "soil": "Sandy Loam",        "advisory": "Kharif and summer groundnut both suitable"},
            {"crop_name": "Groundnut", "district": "Jamnagar",    "suitability": "Highly Suitable",     "score": 88, "seasons": "Kharif", "soil": "Sandy Loam",        "advisory": "ATDR-1 and GG-20 recommended"},
            {"crop_name": "Groundnut", "district": "Bhavnagar",   "suitability": "Moderately Suitable", "score": 80, "seasons": "Kharif", "soil": "Sandy Loam, Black", "advisory": "Drainage essential to prevent collar rot"},
            # Cotton - Saurashtra and Central
            {"crop_name": "Cotton (Kapas)", "district": "Surendranagar", "suitability": "Highly Suitable", "score": 95, "seasons": "Kharif", "soil": "Black", "advisory": "India's largest cotton district. Bt-Cotton (BG-II) preferred"},
            {"crop_name": "Cotton (Kapas)", "district": "Rajkot",  "suitability": "Highly Suitable",    "score": 92, "seasons": "Kharif", "soil": "Black", "advisory": "Drip irrigation increases yield significantly"},
            {"crop_name": "Cotton (Kapas)", "district": "Bhavnagar","suitability": "Highly Suitable",   "score": 90, "seasons": "Kharif", "soil": "Black", "advisory": "Mech-picking possible with uniform variety"},
            {"crop_name": "Cotton (Kapas)", "district": "Vadodara", "suitability": "Moderately Suitable","score": 75, "seasons": "Kharif", "soil": "Black, Clay Loam", "advisory": "Watch for Pink Bollworm in eastern districts"},
            # Cumin - Major spice districts
            {"crop_name": "Cumin (Jeera)", "district": "Patan",    "suitability": "Highly Suitable",    "score": 95, "seasons": "Rabi", "soil": "Sandy Loam", "advisory": "APMC Unjha nearby for direct marketing"},
            {"crop_name": "Cumin (Jeera)", "district": "Banaskantha","suitability": "Highly Suitable",  "score": 93, "seasons": "Rabi", "soil": "Sandy Loam", "advisory": "GJ-4 and GJ-5 varieties recommended. Use sprinkler to prevent blight"},
            {"crop_name": "Cumin (Jeera)", "district": "Mehsana",   "suitability": "Highly Suitable",   "score": 90, "seasons": "Rabi", "soil": "Sandy Loam", "advisory": "Avoid excess irrigation. 2-3 light sprinkler applications"},
            {"crop_name": "Cumin (Jeera)", "district": "Rajkot",    "suitability": "Moderately Suitable","score": 75, "seasons": "Rabi", "soil": "Sandy Loam", "advisory": "Use certified seed to avoid blight"},
            # Castor - North Gujarat
            {"crop_name": "Castor",        "district": "Mehsana",   "suitability": "Highly Suitable",   "score": 95, "seasons": "Kharif", "soil": "Sandy Loam", "advisory": "GCH-7 hybrid recommended. World's castor capital"},
            {"crop_name": "Castor",        "district": "Banaskantha","suitability": "Highly Suitable",  "score": 92, "seasons": "Kharif", "soil": "Sandy Loam", "advisory": "Drip irrigation increases castor yield by 40%"},
            {"crop_name": "Castor",        "district": "Gandhinagar","suitability": "Highly Suitable",  "score": 88, "seasons": "Kharif", "soil": "Sandy Loam", "advisory": "Intercroping with groundnut or cumin possible"},
            {"crop_name": "Castor",        "district": "Bhavnagar", "suitability": "Moderately Suitable","score": 78, "seasons": "Kharif", "soil": "Sandy Loam, Black", "advisory": "Risk of wilt in heavy black soils"},
            # Wheat - North Gujarat
            {"crop_name": "Wheat",         "district": "Banaskantha","suitability": "Highly Suitable",  "score": 92, "seasons": "Rabi", "soil": "Alluvial, Sandy Loam", "advisory": "GW-496, HD-2781 recommended. CZ NARI varieties also good"},
            {"crop_name": "Wheat",         "district": "Patan",     "suitability": "Highly Suitable",   "score": 90, "seasons": "Rabi", "soil": "Alluvial",      "advisory": "Timely sowing (Nov 15-Dec 15) critical for yield"},
            {"crop_name": "Wheat",         "district": "Gandhinagar","suitability": "Highly Suitable",  "score": 88, "seasons": "Rabi", "soil": "Alluvial, Black","advisory": "Sprinkler irrigation reduces water use by 30%"},
            # Mango - Junagadh and Saurashtra
            {"crop_name": "Mango (Kesar / Alphonso)", "district": "Junagadh", "suitability": "Highly Suitable", "score": 98, "seasons": "Perennial", "soil": "Sandy Loam", "advisory": "Kesar GI Tag area. Talala Gir belt is prime location"},
            {"crop_name": "Mango (Kesar / Alphonso)", "district": "Amreli",   "suitability": "Highly Suitable", "score": 90, "seasons": "Perennial", "soil": "Sandy Loam", "advisory": "Kesar variety most profitable. Drip mandatory for quality fruit"},
            {"crop_name": "Mango (Kesar / Alphonso)", "district": "Gir Somnath", "suitability": "Highly Suitable", "score": 95, "seasons": "Perennial", "soil": "Sandy Loam", "advisory": "Best Kesar mangoes in world. Manage hoppers with Imidacloprid"},
            # Sapota - Valsad/Navsari
            {"crop_name": "Sapota (Chikoo)","district": "Valsad",   "suitability": "Highly Suitable",   "score": 97, "seasons": "Perennial", "soil": "Sandy Loam, Alluvial", "advisory": "India's sapota capital. Kalipatti variety most popular"},
            {"crop_name": "Sapota (Chikoo)","district": "Navsari",  "suitability": "Highly Suitable",   "score": 93, "seasons": "Perennial", "soil": "Sandy Loam, Alluvial", "advisory": "APMC Bilimora handles bulk sapota trade"},
            # Banana - Anand, Kheda
            {"crop_name": "Banana",        "district": "Anand",     "suitability": "Highly Suitable",   "score": 95, "seasons": "Perennial", "soil": "Sandy Loam, Clay Loam", "advisory": "G9 tissue culture variety most popular. Drip with fertigation essential"},
            {"crop_name": "Banana",        "district": "Kheda",     "suitability": "Highly Suitable",   "score": 90, "seasons": "Perennial", "soil": "Sandy Loam, Clay Loam", "advisory": "High water use crop. Tube well or canal water essential"},
            {"crop_name": "Banana",        "district": "Bharuch",   "suitability": "Moderately Suitable","score": 80, "seasons": "Perennial", "soil": "Sandy Loam", "advisory": "Dwarf Cavendish also grown. Avoid Fusarium prone areas"},
            # Isabgol - North Gujarat
            {"crop_name": "Isabgol (Psyllium)", "district": "Banaskantha", "suitability": "Highly Suitable", "score": 95, "seasons": "Rabi", "soil": "Sandy Loam, Sandy", "advisory": "Deesa/Dhanera tract is global isabgol belt. Sprinkler only - avoid flooding"},
            {"crop_name": "Isabgol (Psyllium)", "district": "Patan",       "suitability": "Highly Suitable", "score": 90, "seasons": "Rabi", "soil": "Sandy Loam", "advisory": "GI-1 variety recommended. Avoid high humidity areas"},
            # Sugarcane - South Gujarat
            {"crop_name": "Sugarcane",     "district": "Surat",     "suitability": "Highly Suitable",   "score": 90, "seasons": "Annual", "soil": "Alluvial, Sandy Loam", "advisory": "Co-671, CoJ-64 varieties recommended. Drip with fertigation"},
            {"crop_name": "Sugarcane",     "district": "Bharuch",   "suitability": "Highly Suitable",   "score": 85, "seasons": "Annual", "soil": "Alluvial",   "advisory": "Sugar mills available in Ankleshwar and Bharuch areas"},
            {"crop_name": "Sugarcane",     "district": "Narmada",   "suitability": "Moderately Suitable","score": 78, "seasons": "Annual", "soil": "Sandy Loam", "advisory": "Irrigation infrastructure critical for yield stability"},
            # Paddy - South Gujarat
            {"crop_name": "Paddy (Rice)",  "district": "Valsad",    "suitability": "Highly Suitable",   "score": 92, "seasons": "Kharif", "soil": "Clay Loam, Black", "advisory": "GR-11, GNR-1 recommended. SRI method increases yield"},
            {"crop_name": "Paddy (Rice)",  "district": "Navsari",   "suitability": "Highly Suitable",   "score": 90, "seasons": "Kharif", "soil": "Clay Loam", "advisory": "High rainfall zone. Local varieties also popular"},
            {"crop_name": "Paddy (Rice)",  "district": "Dang",      "suitability": "Highly Suitable",   "score": 85, "seasons": "Kharif", "soil": "Red, Laterite", "advisory": "Tribal region. Traditional varieties maintained"},
        ]

        suit_created = 0
        for s in SUITABILITIES:
            crop_obj = Crop.objects.filter(crop_name=s["crop_name"]).first()
            if not crop_obj:
                continue
            obj, created = CropLocationSuitability.objects.get_or_create(
                crop=crop_obj,
                state="Gujarat",
                district=s["district"],
                taluka=None,
                defaults={
                    "suitability_level": s["suitability"],
                    "suitability_score": s["score"],
                    "favorable_seasons": s["seasons"],
                    "recommended_soil_types": s["soil"],
                    "agronomic_advisory": s.get("advisory", ""),
                    "data_source": SRC,
                    "data_type": "Scientific Survey",
                    "reference_date": REF,
                }
            )
            if created:
                suit_created += 1

        self.stdout.write(f"  CropLocationSuitability: {suit_created} created. Total: {CropLocationSuitability.objects.count()}")

        self.stdout.write(self.style.SUCCESS(
            f"\nPhase 4 Complete! "
            f"Categories: {CropCategory.objects.count()}, "
            f"Crops: {Crop.objects.count()}, "
            f"SeasonCalendars: {CropSeasonCalendar.objects.count()}, "
            f"LocationSuitability: {CropLocationSuitability.objects.count()}"
        ))
