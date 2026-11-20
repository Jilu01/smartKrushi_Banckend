from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


class MarketPricesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        crop_filter = request.query_params.get('crop', '').lower()
        district_filter = request.query_params.get('district', '').lower()

        prices = [
            {
                "id": 1,
                "crop_name": "Wheat (ઘઉં)",
                "crop_name_gu": "ઘઉં",
                "crop_name_hi": "गेहूं",
                "variety": "Lokwan / Sharbati",
                "mandi": "APMC Rajkot",
                "district": "Rajkot",
                "state": "Gujarat",
                "modal_price": 2450,
                "min_price": 2200,
                "max_price": 2650,
                "unit": "Quintal",
                "trend": "up",
                "change_pct": 2.5,
                "change_text": "+2.5%",
                "date": "2026-10-10"
            },
            {
                "id": 2,
                "crop_name": "Cotton (કપાસ)",
                "crop_name_gu": "કપાસ",
                "crop_name_hi": "कपास",
                "variety": "Shankar-6",
                "mandi": "APMC Amreli",
                "district": "Amreli",
                "state": "Gujarat",
                "modal_price": 7120,
                "min_price": 6800,
                "max_price": 7400,
                "unit": "Quintal",
                "trend": "up",
                "change_pct": 1.8,
                "change_text": "+1.8%",
                "date": "2026-10-10"
            },
            {
                "id": 3,
                "crop_name": "Groundnut (મગફળી)",
                "crop_name_gu": "મગફળી",
                "crop_name_hi": "मूंगफली",
                "variety": "GG-20",
                "mandi": "APMC Junagadh",
                "district": "Junagadh",
                "state": "Gujarat",
                "modal_price": 6350,
                "min_price": 6000,
                "max_price": 6600,
                "unit": "Quintal",
                "trend": "down",
                "change_pct": -0.8,
                "change_text": "-0.8%",
                "date": "2026-10-10"
            },
            {
                "id": 4,
                "crop_name": "Castor (એરંડા)",
                "crop_name_gu": "એરંડા",
                "crop_name_hi": "अरंडी",
                "variety": "Hybrid-4",
                "mandi": "APMC Mehsana",
                "district": "Mehsana",
                "state": "Gujarat",
                "modal_price": 5980,
                "min_price": 5750,
                "max_price": 6150,
                "unit": "Quintal",
                "trend": "flat",
                "change_pct": 0.0,
                "change_text": "0.0%",
                "date": "2026-10-10"
            },
            {
                "id": 5,
                "crop_name": "Cumin (જીરું)",
                "crop_name_gu": "જીરું",
                "crop_name_hi": "जीरा",
                "variety": "GC-4",
                "mandi": "APMC Unjha",
                "district": "Unjha",
                "state": "Gujarat",
                "modal_price": 28500,
                "min_price": 27000,
                "max_price": 30000,
                "unit": "Quintal",
                "trend": "up",
                "change_pct": 3.2,
                "change_text": "+3.2%",
                "date": "2026-10-10"
            }
        ]

        if crop_filter:
            prices = [p for p in prices if crop_filter in p["crop_name"].lower() or crop_filter in p["crop_name_gu"].lower()]
        if district_filter:
            prices = [p for p in prices if district_filter in p["district"].lower() or district_filter in p["mandi"].lower()]

        return Response(prices)


class GovernmentSchemesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        state = request.query_params.get('state', 'Gujarat')

        schemes = [
            {
                "id": 1,
                "name": "PM-KISAN Samman Nidhi",
                "name_gu": "પીએમ કિસાન સન્માન નિધિ",
                "name_hi": "पीएम किसान सम्मान निधि",
                "description": "Direct income support of ₹6,000 per year in 3 equal installments for all landholding farmer families.",
                "description_gu": "તમામ જમીન ધરાવતા ખેડૂત પરિવારો માટે પ્રતિ વર્ષ ₹6,000 ની સીધી આવક સહાય.",
                "description_hi": "सभी भूमिधारक किसान परिवारों के लिए प्रति वर्ष ₹6,000 की प्रत्यक्ष आय सहायता।",
                "priority": "high",
                "benefit_amount": "₹6,000 / year",
                "apply_url": "https://pmkisan.gov.in/",
                "eligible_criteria": "Small and marginal farmers with land records."
            },
            {
                "id": 2,
                "name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
                "name_gu": "પ્રધાનમંત્રી ફસલ બીમા યોજના",
                "name_hi": "प्रधानमंत्री फसल बीमा योजना",
                "description": "Comprehensive crop insurance protection against yield losses due to non-preventable natural risks.",
                "description_gu": "બિન-નિવારી શકાય તેવા કુદરતી જોખમોને કારણે ઉપજમાં થતા નુકસાન સામે વ્યાપક પાક વીમા સંરક્ષણ.",
                "description_hi": "अप्रतिरोध्य प्राकृतिक जोखिमों के कारण उपज में नुकसान के खिलाफ व्यापक फसल बीमा सुरक्षा।",
                "priority": "high",
                "benefit_amount": "Up to 90% premium subsidy",
                "apply_url": "https://pmfby.gov.in/",
                "eligible_criteria": "All farmers growing notified crops in notified areas."
              },
            {
                "id": 3,
                "name": "Kisan Credit Card (KCC) Scheme",
                "name_gu": "કિસાન ક્રેડિટ કાર્ડ યોજના",
                "name_hi": "किसान क्रेडिट कार्ड योजना",
                "description": "Concessional institutional credit at 4% interest rate with prompt repayment incentive for crop production.",
                "description_gu": "પાક ઉત્પાદન માટે ત્વરિત પુનઃચુકવણી પ્રોત્સાહન સાથે 4% વ્યાજ દરે રાહતસહિત સંસ્થાકીય ધિરાણ.",
                "description_hi": "फसल उत्पादन के लिए त्वरित पुनर्भुगतान प्रोत्साहन के साथ 4% ब्याज दर पर रियायती संस्थागत ऋण।",
                "priority": "medium",
                "benefit_amount": "Credit limit up to ₹3 Lakhs at 4%",
                "apply_url": "https://www.myscheme.gov.in/schemes/kcc",
                "eligible_criteria": "Owner cultivators, tenant farmers, and SHGs."
            },
            {
                "id": 4,
                "name": "Soil Health Card Scheme",
                "name_gu": "સોઇલ હેલ્થ કાર્ડ યોજના",
                "name_hi": "मृदा स्वास्थ्य कार्ड योजना",
                "description": "Free soil testing and customized nutrient recommendation cards for optimizing fertilizer dosage.",
                "description_gu": "ખાતરના ડોઝને ઓપ્ટિમાઇઝ કરવા માટે મફત માટી પરીક્ષણ અને કસ્ટમાઇઝ્ડ પોષક ભલામણ કાર્ડ.",
                "description_hi": "उर्वरक की खुराक को अनुकूलित करने के लिए मुफ्त मिट्टी परीक्षण और अनुकूलित पोषक तत्व सिफारिश कार्ड।",
                "priority": "medium",
                "benefit_amount": "Free Soil Analysis & Dosage Card",
                "apply_url": "https://soilhealth.dac.gov.in/",
                "eligible_criteria": "All agricultural landowners across all states."
            }
        ]

        return Response(schemes)


class CropCalendarView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        calendar = [
            {
                "id": 1,
                "season": "Kharif",
                "months": "June - October",
                "recommended_crops": ["Cotton", "Groundnut", "Rice", "Maize"],
                "sowing_tips": "Ensure deep ploughing before monsoon. Maintain proper drainage to prevent waterlogging."
            },
            {
                "id": 2,
                "season": "Rabi",
                "months": "October - March",
                "recommended_crops": ["Wheat", "Mustard", "Cumin", "Chickpea"],
                "sowing_tips": "Irrigate fields adequately after seed germination. Apply recommended NPK fertilizer doses."
            },
            {
                "id": 3,
                "season": "Zaid",
                "months": "March - June",
                "recommended_crops": ["Watermelon", "Cucumber", "Fodder Crops", "Pulses"],
                "sowing_tips": "Use drip irrigation for efficient water consumption during peak summer temperatures."
            }
        ]
        return Response(calendar)
