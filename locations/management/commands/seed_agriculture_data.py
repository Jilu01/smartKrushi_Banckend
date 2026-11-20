import datetime
from django.core.management.base import BaseCommand
from locations.models import State, District, Taluka, Village
from crops.models import Crop, CropRecord, CropData
from soil.models import SoilRecord, District as LegacyDistrict
from fertilizers.models import Fertilizer
from plant_health.models import PlantDisease, Pest
from weather.models import WeatherRecord


class Command(BaseCommand):
    help = "Seeds initial agricultural data for Gujarat locations, crops, fertilizers, diseases, and soil records"

    def handle(self, *args, **options):
        self.stdout.write("Starting agriculture data seeding...")

        # 1. State: Gujarat
        gujarat, _ = State.objects.get_or_create(
            state_name="Gujarat",
            defaults={"latitude": 22.2587, "longitude": 71.1924}
        )

        # 2. Districts & Talukas
        district_data = {
            "Valsad": {
                "lat": 20.6105, "lon": 72.9258,
                "talukas": ["Valsad", "Pardi", "Umbergaon", "Dharampur", "Kaprada"],
                "villages": ["Killa-Pardi", "Tithal", "Abrama", "Bhagdawada", "Dungri"]
            },
            "Ahmedabad": {
                "lat": 23.0225, "lon": 72.5714,
                "talukas": ["Ahmedabad City", "Daskroi", "Sanand", "Bavla", "Dholka", "Viramgam"],
                "villages": ["Bopal", "Changodar", "Sanand Rural", "Chandial", "Bareja"]
            },
            "Surat": {
                "lat": 21.1702, "lon": 72.8311,
                "talukas": ["Surat City", "Olpad", "Mangrol", "Mandvi", "Kamrej", "Bardoli"],
                "villages": ["Sayan", "Kim", "Mahuva", "Kadod", "Palsana"]
            },
            "Rajkot": {
                "lat": 22.3039, "lon": 70.8022,
                "talukas": ["Rajkot", "Gondal", "Jetpur", "Dhoraji", "Upleta", "Jasdan"],
                "villages": ["Kuvadva", "Ribda", "Shapar", "Bhadla", "Virpur"]
            },
            "Vadodara": {
                "lat": 22.3072, "lon": 73.1812,
                "talukas": ["Vadodara", "Padra", "Karjan", "Dabhoi", "Savli", "Waghodia"],
                "villages": ["Chhani", "Atladara", "Jarod", "Por", "Mobha"]
            },
            "Anand": {
                "lat": 22.5645, "lon": 72.9289,
                "talukas": ["Anand", "Petlad", "Borsad", "Khambhat", "Tarapur", "Umreth"],
                "villages": ["Mogri", "Vasad", "Karamsad", "Vallabh Vidyanagar", "Bakrol"]
            },
            "Bhavnagar": {
                "lat": 21.7645, "lon": 72.1519,
                "talukas": ["Bhavnagar", "Sihor", "Palitana", "Talaja", "Mahuva", "Gadhada"],
                "villages": ["Vartej", "Bhandariya", "Songadh", "Trapaj"]
            },
            "Junagadh": {
                "lat": 21.5222, "lon": 70.4579,
                "talukas": ["Junagadh", "Keshod", "Mangrol", "Visavadar", "Manavadar", "Malia"],
                "villages": ["Vadal", "Bilkha", "Khamdhrol", "Sil"]
            },
            "Mehsana": {
                "lat": 23.5880, "lon": 72.3693,
                "talukas": ["Mehsana", "Kadi", "Visnagar", "Unjha", "Vadnagar", "Vijapur"],
                "villages": ["Panchot", "Kheralu", "Motidau", "Nandasan"]
            },
            "Banaskantha": {
                "lat": 24.1724, "lon": 72.4346,
                "talukas": ["Palanpur", "Deesa", "Dhanera", "Tharad", "Vav", "Dantiwada"],
                "villages": ["Chandisar", "Gadh", "Bhildi", "Malagadh"]
            },
            "Gandhinagar": {
                "lat": 23.2156, "lon": 72.6369,
                "talukas": ["Gandhinagar", "Kalol", "Dahegam", "Mansa"],
                "villages": ["Pethapur", "Chiloda", "Vavol", "Koba"]
            },
            "Jamnagar": {
                "lat": 22.4707, "lon": 70.0577,
                "talukas": ["Jamnagar", "Lalpur", "Jamjodhpur", "Jodiya", "Dhrol"],
                "villages": ["Bed", "Aliabada", "Sikka", "Chela"]
            },
            "Amreli": {
                "lat": 21.6032, "lon": 71.2221,
                "talukas": ["Amreli", "Dhari", "Babra", "Lathi", "Rajula", "Savarkundla"],
                "villages": ["Chalala", "Mota Gokharwala", "Dudhai", "Khambha"]
            },
            "Kutch": {
                "lat": 23.2420, "lon": 69.6669,
                "talukas": ["Bhuj", "Anjar", "Mandvi", "Mundra", "Gandhidham", "Nakhatrana", "Rapar"],
                "villages": ["Madhapar", "Kukma", "Deshalpar", "Kotda"]
            },
            "Bharuch": {
                "lat": 21.7051, "lon": 72.9959,
                "talukas": ["Bharuch", "Ankleshwar", "Jambusar", "Hansot", "Vagra", "Amod"],
                "villages": ["Dahej", "Shuklatirth", "Zadheshwar", "Nabipur"]
            },
            "Navsari": {
                "lat": 20.9467, "lon": 72.9520,
                "talukas": ["Navsari", "Jalalpore", "Gandevi", "Chikhli", "Vansda"],
                "villages": ["Bilimora", "Mahuva", "Amalsad", "Abrama"]
            },
            "Surendranagar": {
                "lat": 22.7275, "lon": 71.6370,
                "talukas": ["Wadhwan", "Dhrangadhra", "Limbdi", "Chotila", "Dasada", "Patdi"],
                "villages": ["Dudhrej", "Sayla", "Muli", "Bhadreshwar"]
            },
            "Patan": {
                "lat": 23.8493, "lon": 72.1266,
                "talukas": ["Patan", "Sidhpur", "Chanasma", "Radhanpur", "Harij", "Sami"],
                "villages": ["Balisana", "Ranuj", "Sankhari", "Vaghel"]
            },
            "Dahod": {
                "lat": 22.8373, "lon": 74.2543,
                "talukas": ["Dahod", "Garbada", "Limkheda", "Jhalod", "Fatepura"],
                "villages": ["Rachhva", "Katwara", "Bordi", "Bavka"]
            },
            "Panchmahal": {
                "lat": 22.7725, "lon": 73.6149,
                "talukas": ["Godhra", "Halol", "Kalol", "Shehra", "Ghoghamba"],
                "villages": ["Pavagadh", "Vavdi", "Tuwa", "Chhabanpur"]
            },
            "Porbandar": {
                "lat": 21.6417, "lon": 69.6293,
                "talukas": ["Porbandar", "Ranavav", "Kutiyana"],
                "villages": ["Bokhira", "Degam", "Rana Vav Rural", "Adityana"]
            },
            "Gir Somnath": {
                "lat": 20.9042, "lon": 70.3667,
                "talukas": ["Veraval", "Talala", "Kodinar", "Una", "Sutrapada", "Gir Gadhada"],
                "villages": ["Prabhas Patan", "Talala Rural", "Bhalpara", "Delvada"]
            },
            "Morbi": {
                "lat": 22.8120, "lon": 70.8377,
                "talukas": ["Morbi", "Wankaner", "Halvad", "Tankara", "Maliya"],
                "villages": ["Trajpar", "Lilapar", "Lajai", "Makansar"]
            },
            "Botad": {
                "lat": 22.1706, "lon": 71.6669,
                "talukas": ["Botad", "Gadhada", "Barwala", "Ranpur"],
                "villages": ["Salangpur", "Paliyad", "Haddad", "Lathidad"]
            },
            "Devbhumi Dwarka": {
                "lat": 22.2442, "lon": 68.9685,
                "talukas": ["Khambhalia", "Dwarka", "Kalyanpur", "Bhanvad"],
                "villages": ["Okha", "Salaya", "Bhimrana", "Raval"]
            },
            "Kheda": {
                "lat": 22.7516, "lon": 72.6847,
                "talukas": ["Nadiad", "Kheda", "Matar", "Mehmedabad", "Kapadvanj", "Thasra"],
                "villages": ["Vaso", "Alindra", "Uttarsanda", "Palana"]
            },
            "Mahisagar": {
                "lat": 23.1667, "lon": 73.5833,
                "talukas": ["Lunawada", "Santrampur", "Kadana", "Khanpur", "Balasinor", "Virpur"],
                "villages": ["Kothamba", "Malpur Rural", "Vardhari", "Janod"]
            },
            "Aravalli": {
                "lat": 23.5333, "lon": 73.2667,
                "talukas": ["Modasa", "Bhiloda", "Bayad", "Dhansura", "Malpur", "Meghraj"],
                "villages": ["Shamlaji", "Isari", "Tintoi", "Dhamanya"]
            },
            "Chhota Udaipur": {
                "lat": 22.3108, "lon": 74.0117,
                "talukas": ["Chhota Udaipur", "Bodeli", "Sankheda", "Jetpur Pavi", "Kavant", "Nasvadi"],
                "villages": ["Bahadarpur", "Alindra Rural", "Zoz", "Panvad"]
            },
            "Narmada": {
                "lat": 21.8711, "lon": 73.5019,
                "talukas": ["Rajpipla", "Nandod", "Dediapada", "Sagbara", "Tilakwada", "Garudeshwar"],
                "villages": ["Kevadia", "Gora", "Poicha", "Vajiriya"]
            },
            "Tapi": {
                "lat": 21.1219, "lon": 73.4357,
                "talukas": ["Vyara", "Songadh", "Valod", "Nizar", "Uchchhal", "Kukarmunda"],
                "villages": ["Doswada", "Fort Songadh", "Bedchit", "Buhari"]
            },
            "Dang": {
                "lat": 20.8033, "lon": 73.6936,
                "talukas": ["Ahwa", "Waghai", "Subir"],
                "villages": ["Saputara", "Girmal", "Shamgahan", "Mahal"]
            }
        }

        for dist_name, d_info in district_data.items():
            dist, _ = District.objects.get_or_create(
                state=gujarat,
                district_name=dist_name,
                defaults={"latitude": d_info["lat"], "longitude": d_info["lon"]}
            )
            for t_name in d_info["talukas"]:
                tal, _ = Taluka.objects.get_or_create(
                    district=dist,
                    taluka_name=t_name,
                    defaults={"latitude": d_info["lat"], "longitude": d_info["lon"]}
                )
                for v_name in d_info.get("villages", []):
                    Village.objects.get_or_create(
                        taluka=tal,
                        village_name=v_name,
                        defaults={"latitude": d_info["lat"], "longitude": d_info["lon"]}
                    )

        # 3. Master Crops
        crops_data = [
            {
                "crop_name": "Cotton",
                "scientific_name": "Gossypium hirsutum",
                "crop_category": "Fiber",
                "crop_description": "Major commercial cash crop of Gujarat, widely grown in Saurashtra and Central Gujarat.",
                "growing_season": "Kharif",
                "crop_duration_days": 160,
                "suitable_soil": "Black soil, Medium Black, Alluvial",
                "suitable_ph_min": 6.5,
                "suitable_ph_max": 8.0,
                "temperature_min": 21.0,
                "temperature_max": 35.0,
                "water_requirement": "Medium",
                "rainfall_requirement": "500-1000 mm",
                "fertilizer_requirement": "120:60:60 N:P2O5:K2O kg/ha",
                "sowing_period": "June - July",
                "harvesting_period": "November - February",
                "irrigation_method": "Drip irrigation or alternate furrow",
                "common_diseases": "Bacterial blight, Alternaria leaf spot, Root rot"
            },
            {
                "crop_name": "Groundnut",
                "scientific_name": "Arachis hypogaea",
                "crop_category": "Oilseed",
                "crop_description": "Crucial oilseed crop of Saurashtra region with high economic value.",
                "growing_season": "Kharif",
                "crop_duration_days": 110,
                "suitable_soil": "Sandy Loam, Light Black soil, Red Loamy",
                "suitable_ph_min": 6.0,
                "suitable_ph_max": 7.5,
                "temperature_min": 20.0,
                "temperature_max": 30.0,
                "water_requirement": "Medium",
                "rainfall_requirement": "500-750 mm",
                "fertilizer_requirement": "25:50:0 N:P2O5:K2O kg/ha + Gypsum 250 kg/ha",
                "sowing_period": "June - July",
                "harvesting_period": "October - November",
                "irrigation_method": "Sprinkler or border check",
                "common_diseases": "Tikka leaf spot, Rust, Collar rot"
            },
            {
                "crop_name": "Wheat",
                "scientific_name": "Triticum aestivum",
                "crop_category": "Cereal",
                "crop_description": "Predominant winter cereal of North and Central Gujarat (Bhal region famed for Bhalia wheat).",
                "growing_season": "Rabi",
                "crop_duration_days": 120,
                "suitable_soil": "Alluvial, Clay Loam, Black soil",
                "suitable_ph_min": 6.0,
                "suitable_ph_max": 7.5,
                "temperature_min": 10.0,
                "temperature_max": 25.0,
                "water_requirement": "Medium",
                "rainfall_requirement": "300-600 mm",
                "fertilizer_requirement": "120:60:40 N:P2O5:K2O kg/ha",
                "sowing_period": "November - December",
                "harvesting_period": "March - April",
                "irrigation_method": "Border strip / Sprinkler (5-6 irrigations)",
                "common_diseases": "Brown rust, Yellow rust, Loose smut, Karnal bunt"
            },
            {
                "crop_name": "Paddy",
                "scientific_name": "Oryza sativa",
                "crop_category": "Cereal",
                "crop_description": "Major staple kharif crop cultivated in South and Central Gujarat.",
                "growing_season": "Kharif",
                "crop_duration_days": 130,
                "suitable_soil": "Clayey, Heavy Black, Alluvial soil",
                "suitable_ph_min": 5.5,
                "suitable_ph_max": 7.2,
                "temperature_min": 20.0,
                "temperature_max": 35.0,
                "water_requirement": "High",
                "rainfall_requirement": "1000-1500 mm",
                "fertilizer_requirement": "100:50:50 N:P2O5:K2O kg/ha + Zinc Sulphate 25 kg/ha",
                "sowing_period": "June (nursery), July (transplanting)",
                "harvesting_period": "October - November",
                "irrigation_method": "Submerged flooding / Alternate wetting and drying (AWD)",
                "common_diseases": "Blast, Bacterial leaf blight, Brown spot, Sheath rot"
            },
            {
                "crop_name": "Sugarcane",
                "scientific_name": "Saccharum officinarum",
                "crop_category": "Cash Crop",
                "crop_description": "Important perennial commercial crop in South Gujarat sugar belt.",
                "growing_season": "Annual",
                "crop_duration_days": 365,
                "suitable_soil": "Deep Alluvial, Clay Loam, Black soil",
                "suitable_ph_min": 6.5,
                "suitable_ph_max": 8.0,
                "temperature_min": 20.0,
                "temperature_max": 38.0,
                "water_requirement": "High",
                "rainfall_requirement": "1200-1800 mm",
                "fertilizer_requirement": "250:125:125 N:P2O5:K2O kg/ha",
                "sowing_period": "October - November / February - March",
                "harvesting_period": "November - March (12 months later)",
                "irrigation_method": "Drip fertigation / Furrow irrigation",
                "common_diseases": "Red rot, Smut, Wilt, Grassy shoot"
            },
            {
                "crop_name": "Cumin",
                "scientific_name": "Cuminum cyminum",
                "crop_category": "Spice",
                "crop_description": "High value seed spice predominantly grown in North Gujarat and Saurashtra (Unjha APMC hub).",
                "growing_season": "Rabi",
                "crop_duration_days": 105,
                "suitable_soil": "Sandy Loam, Well-drained Loam",
                "suitable_ph_min": 6.5,
                "suitable_ph_max": 7.8,
                "temperature_min": 10.0,
                "temperature_max": 26.0,
                "water_requirement": "Low",
                "rainfall_requirement": "200-350 mm",
                "fertilizer_requirement": "30:15:0 N:P2O5:K2O kg/ha",
                "sowing_period": "November",
                "harvesting_period": "February - March",
                "irrigation_method": "Light sprinkler or small furrow (avoid over-watering)",
                "common_diseases": "Blight (Alternaria burnsii), Wilt (Fusarium), Powdery mildew"
            },
            {
                "crop_name": "Castor",
                "scientific_name": "Ricinus communis",
                "crop_category": "Oilseed",
                "crop_description": "Gujarat is the world leader in castor production, largely grown in North Gujarat and Saurashtra.",
                "growing_season": "Kharif",
                "crop_duration_days": 180,
                "suitable_soil": "Sandy Loam, Medium Black, Alluvial",
                "suitable_ph_min": 6.0,
                "suitable_ph_max": 7.5,
                "temperature_min": 20.0,
                "temperature_max": 36.0,
                "water_requirement": "Medium",
                "rainfall_requirement": "500-800 mm",
                "fertilizer_requirement": "75:50:0 N:P2O5:K2O kg/ha",
                "sowing_period": "July - August",
                "harvesting_period": "December - March (multiple pickings)",
                "irrigation_method": "Drip or furrow",
                "common_diseases": "Fusarium wilt, Root rot, Seedling blight"
            },
            {
                "crop_name": "Bajra (Pearl Millet)",
                "scientific_name": "Pennisetum glaucum",
                "crop_category": "Cereal",
                "crop_description": "Drought-hardy staple cereal widely grown in North Gujarat, Kutch, and Saurashtra.",
                "growing_season": "Kharif",
                "crop_duration_days": 85,
                "suitable_soil": "Sandy, Sandy Loam, Light Alluvial",
                "suitable_ph_min": 6.5,
                "suitable_ph_max": 8.5,
                "temperature_min": 22.0,
                "temperature_max": 38.0,
                "water_requirement": "Low",
                "rainfall_requirement": "350-500 mm",
                "fertilizer_requirement": "80:40:0 N:P2O5:K2O kg/ha",
                "sowing_period": "June - July / Summer: February - March",
                "harvesting_period": "September - October / Summer: May",
                "irrigation_method": "Rainfed / 2-3 protective irrigations",
                "common_diseases": "Downy mildew (Green ear), Ergot, Smut"
            },
            {
                "crop_name": "Mustard",
                "scientific_name": "Brassica juncea",
                "crop_category": "Oilseed",
                "crop_description": "Prominent Rabi oilseed of North Gujarat (Banaskantha, Patan, Mehsana).",
                "growing_season": "Rabi",
                "crop_duration_days": 110,
                "suitable_soil": "Sandy Loam, Loam, Alluvial",
                "suitable_ph_min": 6.0,
                "suitable_ph_max": 7.5,
                "temperature_min": 10.0,
                "temperature_max": 25.0,
                "water_requirement": "Low",
                "rainfall_requirement": "250-400 mm",
                "fertilizer_requirement": "50:50:0 N:P2O5:K2O kg/ha + 20 kg Sulphur/ha",
                "sowing_period": "October - November",
                "harvesting_period": "February - March",
                "irrigation_method": "Border strip (3 irrigations)",
                "common_diseases": "White rust, Alternaria blight, Downy mildew"
            },
            {
                "crop_name": "Chickpea (Gram)",
                "scientific_name": "Cicer arietinum",
                "crop_category": "Pulse",
                "crop_description": "Major winter pulse of Saurashtra, Central Gujarat, and Bhal region.",
                "growing_season": "Rabi",
                "crop_duration_days": 100,
                "suitable_soil": "Medium Black, Heavy Clay Loam, Alluvial",
                "suitable_ph_min": 6.0,
                "suitable_ph_max": 7.5,
                "temperature_min": 10.0,
                "temperature_max": 28.0,
                "water_requirement": "Low",
                "rainfall_requirement": "300-450 mm",
                "fertilizer_requirement": "20:40:0 N:P2O5:K2O kg/ha (Rhizobium bio-fertilizer)",
                "sowing_period": "October - November",
                "harvesting_period": "January - February",
                "irrigation_method": "Sprinkler / Residual soil moisture (conserved moisture)",
                "common_diseases": "Fusarium wilt, Dry root rot, Ascochyta blight"
            },
            {
                "crop_name": "Mango (Kesar / Alphonso)",
                "scientific_name": "Mangifera indica",
                "crop_category": "Horticulture",
                "crop_description": "World-famous GI-tagged Gir Kesar and Valsad Alphonso mango orchards of Gujarat.",
                "growing_season": "Perennial",
                "crop_duration_days": 365,
                "suitable_soil": "Alluvial, Medium Black, Red Lateritic Loam",
                "suitable_ph_min": 6.0,
                "suitable_ph_max": 7.8,
                "temperature_min": 15.0,
                "temperature_max": 40.0,
                "water_requirement": "Medium",
                "rainfall_requirement": "750-1200 mm",
                "fertilizer_requirement": "500:250:500 g N:P2O5:K2O per bearing tree/year",
                "sowing_period": "Monsoon planting (June - August)",
                "harvesting_period": "April - June",
                "irrigation_method": "Drip irrigation (basin system)",
                "common_diseases": "Powdery mildew, Anthracnose, Mango malformation"
            },
            {
                "crop_name": "Potato",
                "scientific_name": "Solanum tuberosum",
                "crop_category": "Cash Crop",
                "crop_description": "Deesa (Banaskantha) is known as the Potato Capital of India with very high productivity.",
                "growing_season": "Rabi",
                "crop_duration_days": 90,
                "suitable_soil": "Sandy Loam, Well-drained Light Loam",
                "suitable_ph_min": 5.5,
                "suitable_ph_max": 7.0,
                "temperature_min": 12.0,
                "temperature_max": 25.0,
                "water_requirement": "Medium",
                "rainfall_requirement": "300-500 mm",
                "fertilizer_requirement": "150:100:100 N:P2O5:K2O kg/ha",
                "sowing_period": "October - November",
                "harvesting_period": "January - February",
                "irrigation_method": "Sprinkler or furrow irrigation",
                "common_diseases": "Late blight, Early blight, Bacterial wilt"
            },
            {
                "crop_name": "Fennel (Variyali)",
                "scientific_name": "Foeniculum vulgare",
                "crop_category": "Spice",
                "crop_description": "High-value seed spice primarily grown in North Gujarat (Mehsana, Patan, Banaskantha).",
                "growing_season": "Rabi",
                "crop_duration_days": 150,
                "suitable_soil": "Sandy Loam, Well-drained Loam",
                "suitable_ph_min": 6.5,
                "suitable_ph_max": 8.0,
                "temperature_min": 12.0,
                "temperature_max": 28.0,
                "water_requirement": "Low",
                "rainfall_requirement": "300-500 mm",
                "fertilizer_requirement": "60:30:0 N:P2O5:K2O kg/ha",
                "sowing_period": "October - November (direct or transplanted)",
                "harvesting_period": "March - April",
                "irrigation_method": "Furrow or light sprinkler",
                "common_diseases": "Ramularia blight, Powdery mildew"
            }
        ]

        for c_data in crops_data:
            Crop.objects.get_or_create(
                crop_name=c_data["crop_name"],
                defaults=c_data
            )

        # 4. Master Fertilizers
        fertilizers_data = [
            {
                "fertilizer_name": "Urea (46% N)",
                "fertilizer_type": "Chemical",
                "nitrogen_percentage": 46.0,
                "phosphorus_percentage": 0.0,
                "potassium_percentage": 0.0,
                "sulphur_percentage": 0.0,
                "recommended_crops": "All crops (Wheat, Paddy, Cotton, Sugarcane, Maize)",
                "application_method": "Top dressing / Split broadcasting",
                "dosage_per_hectare": "100-250 kg/ha in 2-3 split doses",
                "application_timing": "Vegetative growth and tillering stage",
                "precautions": "Avoid application during rain or standing water; incorporate into moist soil.",
                "description": "High-analysis nitrogenous synthetic fertilizer supplying vital N for vegetative vigour and chlorophyll synthesis."
            },
            {
                "fertilizer_name": "Di-Ammonium Phosphate (DAP 18:46:0)",
                "fertilizer_type": "Chemical",
                "nitrogen_percentage": 18.0,
                "phosphorus_percentage": 46.0,
                "potassium_percentage": 0.0,
                "sulphur_percentage": 0.0,
                "recommended_crops": "Cereals, Pulses, Oilseeds, Cotton, Groundnut",
                "application_method": "Basal placement in root zone at sowing",
                "dosage_per_hectare": "100-150 kg/ha",
                "application_timing": "At the time of sowing / planting",
                "precautions": "Do not mix with zinc sulphate or alkaline materials.",
                "description": "Widely used phosphatic fertilizer containing 18% Ammoniacal Nitrogen and 46% available P2O5."
            },
            {
                "fertilizer_name": "Muriate of Potash (MOP 0:0:60)",
                "fertilizer_type": "Chemical",
                "nitrogen_percentage": 0.0,
                "phosphorus_percentage": 0.0,
                "potassium_percentage": 60.0,
                "sulphur_percentage": 0.0,
                "recommended_crops": "Sugarcane, Cotton, Wheat, Paddy, Potato, Fruit trees",
                "application_method": "Basal application or split with nitrogen",
                "dosage_per_hectare": "50-100 kg/ha",
                "application_timing": "Basal at sowing and at panicle / boll formation",
                "precautions": "Not recommended for chlorine-sensitive crops like tobacco and grapes.",
                "description": "Primary potassium source (KCl) enhancing disease resistance, stem strength, drought tolerance, and grain luster."
            },
            {
                "fertilizer_name": "Single Super Phosphate (SSP 0:16:0:11S)",
                "fertilizer_type": "Chemical",
                "nitrogen_percentage": 0.0,
                "phosphorus_percentage": 16.0,
                "potassium_percentage": 0.0,
                "sulphur_percentage": 11.0,
                "recommended_crops": "Oilseeds (Groundnut, Mustard, Castor, Soybean) and Pulses",
                "application_method": "Basal application below seed depth",
                "dosage_per_hectare": "150-250 kg/ha",
                "application_timing": "At sowing time",
                "precautions": "Incorporate well into soil to prevent phosphorus fixation.",
                "description": "Rich source of 16% P2O5 and 11% essential Sulphur, crucial for oil content in oilseeds and nodulation in legumes."
            },
            {
                "fertilizer_name": "Vermicompost (Organic)",
                "fertilizer_type": "Organic",
                "nitrogen_percentage": 1.5,
                "phosphorus_percentage": 1.0,
                "potassium_percentage": 1.2,
                "sulphur_percentage": 0.5,
                "recommended_crops": "All crops, Horticulture, Vegetables, Spices, Floriculture",
                "application_method": "Soil incorporation during field preparation",
                "dosage_per_hectare": "2.5 - 5.0 tonnes/ha",
                "application_timing": "Pre-sowing tillage or furrow application",
                "precautions": "Store in shade and maintain adequate moisture.",
                "description": "Earthworm-processed nutrient-rich organic manure loaded with beneficial microflora and plant growth hormones."
            }
        ]

        for f_data in fertilizers_data:
            Fertilizer.objects.get_or_create(
                fertilizer_name=f_data["fertilizer_name"],
                defaults=f_data
            )

        # 5. Master Plant Diseases & Pests
        cotton_crop = Crop.objects.filter(crop_name="Cotton").first()
        wheat_crop = Crop.objects.filter(crop_name="Wheat").first()
        paddy_crop = Crop.objects.filter(crop_name="Paddy").first()

        diseases_data = [
            {
                "crop": cotton_crop,
                "crop_name": "Cotton",
                "disease_name": "Bacterial Blight (Angular Leaf Spot)",
                "disease_category": "Bacterial",
                "symptoms": "Angular water-soaked spots on leaves bounded by veins; black lesions on petioles and bolls (black arm symptom).",
                "causes": "Xanthomonas citri pv. malvacearum; favored by high humidity (85%+) and warm temperatures (30-35°C).",
                "prevention": "Acid delinting of seeds; sow resistant hybrids; maintain field sanitation.",
                "treatment": "Spray Copper Oxychloride 50 WP (2.5 g/L) + Streptocycline (100 mg/L) at first symptom appearance.",
                "affected_plant_parts": "Leaves, Stems, Bolls",
                "severity": "High"
            },
            {
                "crop": wheat_crop,
                "crop_name": "Wheat",
                "disease_name": "Brown / Leaf Rust",
                "disease_category": "Fungal",
                "symptoms": "Small, round orange-brown pustules scattered randomly on leaf blades.",
                "causes": "Puccinia triticina; airborne urediniospores favored by mild temperatures (15-25°C) and dew.",
                "prevention": "Sow rust-resistant varieties (GW-322, GW-496); timely sowing before late November.",
                "treatment": "Foliar spray of Propiconazole 25 EC (1 ml/L) or Tebuconazole 250 EC at first appearance of pustules.",
                "affected_plant_parts": "Leaves, Sheaths",
                "severity": "Critical"
            },
            {
                "crop": paddy_crop,
                "crop_name": "Paddy",
                "disease_name": "Rice Blast",
                "disease_category": "Fungal",
                "symptoms": "Spindle-shaped spots with grey centers and brown margins on leaves; rotting of neck node (neck blast).",
                "causes": "Magnaporthe oryzae (Pyricularia oryzae); promoted by excessive nitrogen and cloudy damp weather.",
                "prevention": "Avoid excessive nitrogen application; seed treatment with Tricyclazole 75 WP (2 g/kg).",
                "treatment": "Spray Tricyclazole 75 WP (0.6 g/L) or Isoprothiolane 40 EC (1.5 ml/L) at boot leaf to heading stage.",
                "affected_plant_parts": "Leaves, Panicle neck, Nodes",
                "severity": "Critical"
            }
        ]

        for d_data in diseases_data:
            PlantDisease.objects.get_or_create(
                disease_name=d_data["disease_name"],
                crop_name=d_data["crop_name"],
                defaults=d_data
            )

        pests_data = [
            {
                "pest_name": "Pink Bollworm",
                "scientific_name": "Pectinophora gossypiella",
                "affected_crops": "Cotton",
                "symptoms": "Rosetted flowers, premature boll opening, stained lint, holes in developing bolls plugged with excreta.",
                "damage_description": "Larvae bore into flower buds and bolls, devouring seeds and degrading fiber quality.",
                "prevention": "Install pheromone traps (5-8 traps/ha); destroy crop residues after final picking.",
                "management_method": "Release Trichogramma egg parasitoids; spray Emamectin Benzoate 5 SG (0.4 g/L) or Chlorantraniliprole 18.5 SC (0.3 ml/L)."
            },
            {
                "pest_name": "Whitefly",
                "scientific_name": "Bemisia tabaci",
                "affected_crops": "Cotton, Groundnut, Tomato, Brinjal, Soybean",
                "symptoms": "Yellowing and curling of leaves, honeydew secretion leading to black sooty mold growth.",
                "damage_description": "Nymphs and adults suck phloem sap, transmitting devastating viral diseases like Cotton Leaf Curl Virus (CLCuV).",
                "prevention": "Install yellow sticky traps (15-20 traps/ha); avoid excessive urea fertilization.",
                "management_method": "Spray Neem oil 1500 ppm (5 ml/L) or Diafenthiuron 50 WP (1.2 g/L) or Pyriproxyfen 10 EC (1.5 ml/L)."
            },
            {
                "pest_name": "Stem Borer (Yellow Stem Borer)",
                "scientific_name": "Scirpophaga incertulas",
                "affected_crops": "Paddy, Maize, Sugarcane",
                "symptoms": "'Dead heart' in vegetative stage and 'White ear head' with empty chaffy grains at panicle emergence.",
                "damage_description": "Caterpillars bore into central leaf whorl and stem, severing the vascular bundle.",
                "prevention": "Clip seedling tips before transplanting to destroy egg masses; install pheromone traps.",
                "management_method": "Apply Cartap Hydrochloride 4G (18-20 kg/ha) or spray Chlorantraniliprole 0.4% G."
            }
        ]

        for p_data in pests_data:
            Pest.objects.get_or_create(
                pest_name=p_data["pest_name"],
                defaults=p_data
            )

        # 6. Sample Soil Records for Gujarat Districts
        sample_soils = [
            {
                "state": "Gujarat", "district": "Valsad", "taluka": "Pardi", "village": "Killa-Pardi",
                "soil_name": "Coastal Alluvial Loam", "soil_type": "Alluvial", "soil_texture": "Sandy Clay Loam",
                "soil_ph": 6.8, "electrical_conductivity": 0.45, "organic_carbon": 0.72,
                "nitrogen": 310.0, "phosphorus": 18.5, "potassium": 210.0,
                "sulphur": 14.0, "zinc": 0.85, "iron": 5.2, "boron": 0.60,
                "sand_percentage": 45.0, "silt_percentage": 25.0, "clay_percentage": 30.0,
                "sample_date": datetime.date(2024, 5, 15),
                "data_source": "Gujarat Soil Health Card Scheme",
                "remarks": "Healthy balanced soil suitable for mango orchards and kharif paddy."
            },
            {
                "state": "Gujarat", "district": "Ahmedabad", "taluka": "Sanand", "village": "Sanand Rural",
                "soil_name": "Medium Black Soil", "soil_type": "Black", "soil_texture": "Clayey",
                "soil_ph": 7.8, "electrical_conductivity": 0.95, "organic_carbon": 0.42,
                "nitrogen": 210.0, "phosphorus": 8.5, "potassium": 290.0,
                "sulphur": 9.0, "zinc": 0.45, "iron": 3.8, "boron": 0.40,
                "sand_percentage": 20.0, "silt_percentage": 30.0, "clay_percentage": 50.0,
                "sample_date": datetime.date(2024, 6, 2),
                "data_source": "District Agriculture Office Ahmedabad",
                "remarks": "Low in Nitrogen, Phosphorus, and Organic Carbon. High moisture retention."
            },
            {
                "state": "Gujarat", "district": "Rajkot", "taluka": "Gondal", "village": "Ribda",
                "soil_name": "Deep Black Soil", "soil_type": "Black", "soil_texture": "Clay Loam",
                "soil_ph": 7.4, "electrical_conductivity": 0.60, "organic_carbon": 0.58,
                "nitrogen": 260.0, "phosphorus": 14.0, "potassium": 340.0,
                "sulphur": 12.0, "zinc": 0.62, "iron": 4.1, "boron": 0.52,
                "sand_percentage": 30.0, "silt_percentage": 30.0, "clay_percentage": 40.0,
                "sample_date": datetime.date(2024, 6, 20),
                "data_source": "Saurashtra University Agricultural Dept",
                "remarks": "Prime soil for Bt cotton and groundnut cultivation."
            },
            {
                "state": "Gujarat", "district": "Surat", "taluka": "Bardoli", "village": "Kadod",
                "soil_name": "Heavy Black Alluvium", "soil_type": "Black", "soil_texture": "Heavy Clay",
                "soil_ph": 7.2, "electrical_conductivity": 0.50, "organic_carbon": 0.85,
                "nitrogen": 340.0, "phosphorus": 22.0, "potassium": 280.0,
                "sulphur": 16.0, "zinc": 0.90, "iron": 6.0, "boron": 0.65,
                "sand_percentage": 15.0, "silt_percentage": 35.0, "clay_percentage": 50.0,
                "sample_date": datetime.date(2024, 4, 10),
                "data_source": "Surat District Cooperative Dairy & Agri Lab",
                "remarks": "Excellent nutrient profile, high organic content, ideal for sugarcane."
            },
            {
                "state": "Gujarat", "district": "Mehsana", "taluka": "Unjha", "village": "Kheralu",
                "soil_name": "Sandy Loam Alluvium", "soil_type": "Sandy Loam", "soil_texture": "Sandy Loam",
                "soil_ph": 7.6, "electrical_conductivity": 0.40, "organic_carbon": 0.35,
                "nitrogen": 190.0, "phosphorus": 12.0, "potassium": 160.0,
                "sulphur": 8.0, "zinc": 0.50, "iron": 3.2, "boron": 0.38,
                "sand_percentage": 65.0, "silt_percentage": 20.0, "clay_percentage": 15.0,
                "sample_date": datetime.date(2024, 5, 28),
                "data_source": "North Gujarat Agro Research Station",
                "remarks": "Light soil with fast drainage. Ideal for cumin, mustard, and castor with drip irrigation."
            },
            # District-level authentic soil profiles for Gujarat districts
            {
                "state": "Gujarat", "district": "Anand", "taluka": None, "village": None,
                "soil_name": "Charotar Alluvial Goradu", "soil_type": "Alluvial", "soil_texture": "Sandy Loam",
                "soil_ph": 7.4, "electrical_conductivity": 0.48, "organic_carbon": 0.52,
                "nitrogen": 230.0, "phosphorus": 16.0, "potassium": 250.0,
                "sulphur": 11.0, "zinc": 0.70, "iron": 4.5, "boron": 0.50,
                "sand_percentage": 50.0, "silt_percentage": 30.0, "clay_percentage": 20.0,
                "sample_date": datetime.date(2024, 6, 10),
                "data_source": "Anand Agricultural University (AAU) Soil Testing Lab",
                "remarks": "Famed fertile Goradu soil of Charotar region. Highly responsive to organic manures."
            },
            {
                "state": "Gujarat", "district": "Vadodara", "taluka": None, "village": None,
                "soil_name": "Medium to Deep Black Soil", "soil_type": "Black", "soil_texture": "Clay Loam",
                "soil_ph": 7.5, "electrical_conductivity": 0.55, "organic_carbon": 0.56,
                "nitrogen": 250.0, "phosphorus": 13.0, "potassium": 270.0,
                "sulphur": 12.0, "zinc": 0.65, "iron": 4.8, "boron": 0.48,
                "sand_percentage": 25.0, "silt_percentage": 35.0, "clay_percentage": 40.0,
                "sample_date": datetime.date(2024, 5, 18),
                "data_source": "Vadodara District Agriculture Office",
                "remarks": "Good moisture retention. Excellent for cotton, pigeonpea, and wheat."
            },
            {
                "state": "Gujarat", "district": "Bhavnagar", "taluka": None, "village": None,
                "soil_name": "Medium Black Coastal Loam", "soil_type": "Black", "soil_texture": "Clayey Loam",
                "soil_ph": 7.8, "electrical_conductivity": 0.80, "organic_carbon": 0.48,
                "nitrogen": 225.0, "phosphorus": 11.0, "potassium": 310.0,
                "sulphur": 10.0, "zinc": 0.55, "iron": 4.0, "boron": 0.45,
                "sand_percentage": 28.0, "silt_percentage": 32.0, "clay_percentage": 40.0,
                "sample_date": datetime.date(2024, 6, 12),
                "data_source": "Bhavnagar District Soil Health Card Scheme",
                "remarks": "High potassium, moderate nitrogen. Onion, cotton, and groundnut favored."
            },
            {
                "state": "Gujarat", "district": "Junagadh", "taluka": None, "village": None,
                "soil_name": "Medium Black Calcareous Soil", "soil_type": "Black", "soil_texture": "Clay Loam",
                "soil_ph": 7.6, "electrical_conductivity": 0.62, "organic_carbon": 0.62,
                "nitrogen": 245.0, "phosphorus": 15.5, "potassium": 330.0,
                "sulphur": 13.0, "zinc": 0.68, "iron": 4.2, "boron": 0.52,
                "sand_percentage": 26.0, "silt_percentage": 34.0, "clay_percentage": 40.0,
                "sample_date": datetime.date(2024, 5, 22),
                "data_source": "Junagadh Agricultural University (JAU) Soil Testing Lab",
                "remarks": "Prime Saurashtra black soil. Renowned for Gir Kesar mango, groundnut, and wheat."
            },
            {
                "state": "Gujarat", "district": "Banaskantha", "taluka": None, "village": None,
                "soil_name": "Sandy to Sandy Loam Alluvium", "soil_type": "Sandy Loam", "soil_texture": "Sandy Loam",
                "soil_ph": 7.9, "electrical_conductivity": 0.42, "organic_carbon": 0.32,
                "nitrogen": 180.0, "phosphorus": 10.5, "potassium": 190.0,
                "sulphur": 7.5, "zinc": 0.48, "iron": 3.0, "boron": 0.35,
                "sand_percentage": 70.0, "silt_percentage": 18.0, "clay_percentage": 12.0,
                "sample_date": datetime.date(2024, 6, 8),
                "data_source": "SDAU Sardarkrushinagar Soil Testing Laboratory",
                "remarks": "Porous sandy soil with excellent drainage. Outstanding for potato, castor, mustard, and bajra under micro-irrigation."
            },
            {
                "state": "Gujarat", "district": "Gandhinagar", "taluka": None, "village": None,
                "soil_name": "Sandy Loam (Goradu)", "soil_type": "Alluvial", "soil_texture": "Sandy Loam",
                "soil_ph": 7.4, "electrical_conductivity": 0.45, "organic_carbon": 0.45,
                "nitrogen": 215.0, "phosphorus": 13.5, "potassium": 230.0,
                "sulphur": 9.5, "zinc": 0.58, "iron": 3.9, "boron": 0.42,
                "sand_percentage": 55.0, "silt_percentage": 28.0, "clay_percentage": 17.0,
                "sample_date": datetime.date(2024, 6, 15),
                "data_source": "Gujarat State Department of Agriculture",
                "remarks": "Good permeability and workable structure. Supports vegetables, wheat, and castor."
            },
            {
                "state": "Gujarat", "district": "Jamnagar", "taluka": None, "village": None,
                "soil_name": "Medium Black to Clay Loam", "soil_type": "Black", "soil_texture": "Clay Loam",
                "soil_ph": 7.7, "electrical_conductivity": 0.65, "organic_carbon": 0.52,
                "nitrogen": 235.0, "phosphorus": 12.0, "potassium": 305.0,
                "sulphur": 11.5, "zinc": 0.60, "iron": 4.1, "boron": 0.46,
                "sand_percentage": 28.0, "silt_percentage": 32.0, "clay_percentage": 40.0,
                "sample_date": datetime.date(2024, 5, 30),
                "data_source": "Saurashtra Agro-Climatic Zone Soil Survey",
                "remarks": "High potassium, moderate nitrogen. Favorable for groundnut, cotton, and garlic."
            },
            {
                "state": "Gujarat", "district": "Amreli", "taluka": None, "village": None,
                "soil_name": "Medium Black Soil", "soil_type": "Black", "soil_texture": "Clay Loam",
                "soil_ph": 7.5, "electrical_conductivity": 0.58, "organic_carbon": 0.54,
                "nitrogen": 245.0, "phosphorus": 13.0, "potassium": 315.0,
                "sulphur": 12.0, "zinc": 0.62, "iron": 4.3, "boron": 0.48,
                "sand_percentage": 27.0, "silt_percentage": 33.0, "clay_percentage": 40.0,
                "sample_date": datetime.date(2024, 6, 5),
                "data_source": "Amreli KVK Soil Testing Center",
                "remarks": "Rich in potassium. Cotton, groundnut, and sesame dominate cultivation."
            },
            {
                "state": "Gujarat", "district": "Kutch", "taluka": None, "village": None,
                "soil_name": "Arid Sandy to Saline Loam", "soil_type": "Desert", "soil_texture": "Sandy Loam",
                "soil_ph": 8.1, "electrical_conductivity": 1.20, "organic_carbon": 0.25,
                "nitrogen": 150.0, "phosphorus": 8.0, "potassium": 210.0,
                "sulphur": 6.5, "zinc": 0.40, "iron": 2.8, "boron": 0.30,
                "sand_percentage": 75.0, "silt_percentage": 15.0, "clay_percentage": 10.0,
                "sample_date": datetime.date(2024, 5, 12),
                "data_source": "Central Arid Zone Soil Research Institute (CAZRI)",
                "remarks": "Arid soil with high salinity potential. Date palm, pomegranate, castor, and cumin flourish under drip."
            },
            {
                "state": "Gujarat", "district": "Bharuch", "taluka": None, "village": None,
                "soil_name": "Deep Black Cotton Soil (Kanham)", "soil_type": "Black", "soil_texture": "Heavy Clay",
                "soil_ph": 7.8, "electrical_conductivity": 0.70, "organic_carbon": 0.65,
                "nitrogen": 265.0, "phosphorus": 14.5, "potassium": 290.0,
                "sulphur": 14.0, "zinc": 0.72, "iron": 5.0, "boron": 0.55,
                "sand_percentage": 15.0, "silt_percentage": 35.0, "clay_percentage": 50.0,
                "sample_date": datetime.date(2024, 4, 25),
                "data_source": "Bharuch District Cotton Soil Research Lab",
                "remarks": "Legendary Kanham deep black soil famed for premier cotton, banana, and pigeonpea."
            },
            {
                "state": "Gujarat", "district": "Navsari", "taluka": None, "village": None,
                "soil_name": "Coastal Deep Black & Alluvial Loam", "soil_type": "Alluvial", "soil_texture": "Clay Loam",
                "soil_ph": 7.0, "electrical_conductivity": 0.48, "organic_carbon": 0.78,
                "nitrogen": 325.0, "phosphorus": 20.0, "potassium": 260.0,
                "sulphur": 15.0, "zinc": 0.88, "iron": 5.8, "boron": 0.62,
                "sand_percentage": 25.0, "silt_percentage": 35.0, "clay_percentage": 40.0,
                "sample_date": datetime.date(2024, 5, 16),
                "data_source": "Navsari Agricultural University (NAU) Soil Science Dept",
                "remarks": "High organic matter and nutrient content. Ideal for sugarcane, paddy, mango, and chikoo."
            },
            {
                "state": "Gujarat", "district": "Dang", "taluka": None, "village": None,
                "soil_name": "Forest Red Lateritic Loam", "soil_type": "Laterite", "soil_texture": "Loam",
                "soil_ph": 6.4, "electrical_conductivity": 0.35, "organic_carbon": 0.95,
                "nitrogen": 330.0, "phosphorus": 14.0, "potassium": 220.0,
                "sulphur": 16.0, "zinc": 0.92, "iron": 6.5, "boron": 0.58,
                "sand_percentage": 40.0, "silt_percentage": 35.0, "clay_percentage": 25.0,
                "sample_date": datetime.date(2024, 5, 10),
                "data_source": "NAU Hill Millet & Forest Agro Research Station, Waghai, Dang",
                "remarks": "High organic carbon, slightly acidic lateritic soil. Ideal for finger millet (Nagli/Ragi), ginger, and rice."
            }
        ]

        for s_data in sample_soils:
            SoilRecord.objects.get_or_create(
                state=s_data["state"],
                district=s_data["district"],
                taluka=s_data.get("taluka"),
                village=s_data.get("village"),
                defaults=s_data
            )

        # 7. Sample Crop Production Records
        sample_crop_records = [
            {"state": "Gujarat", "district": "Valsad", "taluka": "Pardi", "crop_name": "Paddy", "growing_season": "Kharif", "crop_duration_days": 130, "area_hectares": 12000.0, "production_tonnes": 38400.0, "yield_kg_per_hectare": 3200.0, "year": 2024},
            {"state": "Gujarat", "district": "Ahmedabad", "taluka": "Sanand", "crop_name": "Wheat", "growing_season": "Rabi", "crop_duration_days": 120, "area_hectares": 25000.0, "production_tonnes": 87500.0, "yield_kg_per_hectare": 3500.0, "year": 2024},
            {"state": "Gujarat", "district": "Surat", "taluka": "Bardoli", "crop_name": "Sugarcane", "growing_season": "Annual", "crop_duration_days": 365, "area_hectares": 18000.0, "production_tonnes": 1350000.0, "yield_kg_per_hectare": 75000.0, "year": 2024},
            {"state": "Gujarat", "district": "Rajkot", "taluka": "Gondal", "crop_name": "Groundnut", "growing_season": "Kharif", "crop_duration_days": 110, "area_hectares": 45000.0, "production_tonnes": 99000.0, "yield_kg_per_hectare": 2200.0, "year": 2024},
            {"state": "Gujarat", "district": "Rajkot", "taluka": "Jetpur", "crop_name": "Cotton", "growing_season": "Kharif", "crop_duration_days": 160, "area_hectares": 60000.0, "production_tonnes": 132000.0, "yield_kg_per_hectare": 2200.0, "year": 2024},
            {"state": "Gujarat", "district": "Mehsana", "taluka": "Unjha", "crop_name": "Cumin", "growing_season": "Rabi", "crop_duration_days": 105, "area_hectares": 15000.0, "production_tonnes": 12000.0, "yield_kg_per_hectare": 800.0, "year": 2024},
        ]

        for cr_data in sample_crop_records:
            CropRecord.objects.get_or_create(
                state=cr_data["state"],
                district=cr_data["district"],
                crop_name=cr_data["crop_name"],
                year=cr_data["year"],
                defaults=cr_data
            )

        # 8. Sample Weather Records
        sample_weather = [
            {"state": "Gujarat", "district": "Ahmedabad", "latitude": 23.0225, "longitude": 72.5714, "temperature": 32.5, "feels_like": 34.0, "humidity": 45.0, "rainfall": 0.0, "wind_speed": 12.0, "weather_condition": "Clear sky", "recorded_at": datetime.datetime(2024, 10, 1, 10, 0, tzinfo=datetime.timezone.utc), "data_source": "Open-Meteo API", "is_manual": False},
            {"state": "Gujarat", "district": "Valsad", "latitude": 20.6105, "longitude": 72.9258, "temperature": 29.0, "feels_like": 32.0, "humidity": 78.0, "rainfall": 2.5, "wind_speed": 15.0, "weather_condition": "Light drizzle", "recorded_at": datetime.datetime(2024, 10, 1, 10, 0, tzinfo=datetime.timezone.utc), "data_source": "Open-Meteo API", "is_manual": False},
            {"state": "Gujarat", "district": "Rajkot", "latitude": 22.3039, "longitude": 70.8022, "temperature": 34.0, "feels_like": 36.0, "humidity": 40.0, "rainfall": 0.0, "wind_speed": 10.0, "weather_condition": "Mainly clear", "recorded_at": datetime.datetime(2024, 10, 1, 10, 0, tzinfo=datetime.timezone.utc), "data_source": "Open-Meteo API", "is_manual": False},
        ]

        for w_data in sample_weather:
            WeatherRecord.objects.get_or_create(
                latitude=w_data["latitude"],
                longitude=w_data["longitude"],
                recorded_at=w_data["recorded_at"],
                defaults=w_data
            )

        self.stdout.write(self.style.SUCCESS("Agricultural master and sample data successfully seeded!"))
