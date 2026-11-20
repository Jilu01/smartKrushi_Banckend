from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db.models import Q
from .models import Fertilizer
from .serializers import FertilizerSerializer
from soil.models import SoilRecord


class FertilizerViewSet(viewsets.ModelViewSet):
    queryset = Fertilizer.objects.all()
    serializer_class = FertilizerSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['fertilizer_name', 'fertilizer_type', 'recommended_crops', 'description']
    ordering_fields = ['fertilizer_name', 'nitrogen_percentage', 'phosphorus_percentage', 'potassium_percentage']

    def get_queryset(self):
        qs = super().get_queryset()
        f_type = self.request.query_params.get('type') or self.request.query_params.get('fertilizer_type')
        if f_type:
            qs = qs.filter(fertilizer_type__icontains=f_type)
        return qs

    @action(detail=False, methods=['get'], url_path='by-crop')
    def by_crop(self, request):
        crop = request.query_params.get('crop') or request.query_params.get('crop_name')
        if not crop:
            return Response(
                {"error": "Please provide 'crop' or 'crop_name' query parameter (e.g. wheat, paddy, cotton)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Match specific crop or general categories like 'all crops', 'cereals'
        qs = self.get_queryset().filter(
            Q(recommended_crops__icontains=crop) |
            Q(recommended_crops__icontains='all') |
            Q(recommended_crops__isnull=True)
        )

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(self.get_serializer(qs, many=True).data)

    @action(detail=False, methods=['get', 'post'], url_path='recommend')
    def recommend(self, request):
        """
        POST /api/fertilizers/recommend/ or GET /api/fertilizers/recommend/
        """
        return self.recommendations(request)

    @action(detail=False, methods=['get', 'post'], url_path='recommendations')
    def recommendations(self, request):
        """
        GET /api/fertilizers/recommendations/?location_id=&crop_id=&village_id=&taluka_id=&district_id=
        Location-specific fertilizer recommendations derived from:
        - Soil NPK, pH, and Organic Carbon values (from hierarchical location soil lookup)
        - Selected crop agronomic nutrient requirements
        - University Package of Practices
        """
        from soil.views import resolve_hierarchical_soil
        from crops.models import Crop

        data = request.data if request.method == 'POST' else request.query_params

        crop_id = data.get('crop_id')
        crop_name = data.get('crop_name') or data.get('crop')
        village_id = data.get('village_id')
        taluka_id = data.get('taluka_id')
        district_id = data.get('district_id') or data.get('location_id')
        village = data.get('village')
        taluka = data.get('taluka')
        district = data.get('district')
        lat = data.get('latitude') or data.get('lat')
        lon = data.get('longitude') or data.get('lon')
        soil_id = data.get('soil_id')

        # 1. Resolve crop details if specified
        crop_obj = None
        if crop_id:
            crop_obj = Crop.objects.filter(id=crop_id).first()
            if crop_obj:
                crop_name = crop_obj.crop_name
        elif crop_name:
            crop_obj = Crop.objects.filter(crop_name__icontains=crop_name.strip()).first()

        # 2. Resolve Soil Data using hierarchical resolver
        soil_res = resolve_hierarchical_soil(
            village_id=village_id,
            taluka_id=taluka_id,
            district_id=district_id,
            village_name=village,
            taluka_name=taluka,
            district_name=district,
            lat=lat,
            lon=lon
        )

        soil_rec = soil_res["record"]
        res_level = soil_res["resolution_level"]
        data_level_notice = soil_res["data_level_notice"]
        resolved_district = soil_res["target_district"]
        resolved_taluka = soil_res["target_taluka"]
        resolved_village = soil_res["target_village"]

        soil_n = soil_rec.nitrogen if soil_rec else None
        soil_p = soil_rec.phosphorus if soil_rec else None
        soil_k = soil_rec.potassium if soil_rec else None
        soil_ph = soil_rec.soil_ph if soil_rec else None
        soil_oc = soil_rec.organic_carbon if soil_rec else None

        # Allow explicit numeric overrides if passed
        try:
            if data.get('nitrogen') is not None or data.get('n') is not None:
                soil_n = float(data.get('nitrogen') or data.get('n'))
            if data.get('phosphorus') is not None or data.get('p') is not None:
                soil_p = float(data.get('phosphorus') or data.get('p'))
            if data.get('potassium') is not None or data.get('k') is not None:
                soil_k = float(data.get('potassium') or data.get('k'))
            if data.get('soil_ph') is not None or data.get('ph') is not None:
                soil_ph = float(data.get('soil_ph') or data.get('ph'))
            if data.get('organic_carbon') is not None or data.get('oc') is not None:
                soil_oc = float(data.get('organic_carbon') or data.get('oc'))
        except (ValueError, TypeError):
            pass

        suggested_fertilizers = []
        guidelines = []
        deficiencies = []
        cautions = []

        # Evaluate Nitrogen
        if soil_n is not None:
            if soil_n < 280:
                deficiencies.append({
                    "nutrient": "Nitrogen (N)",
                    "status": "Low (<280 kg/ha)",
                    "value": f"{soil_n} kg/ha",
                    "reason": f"Available soil Nitrogen is deficient ({soil_n} kg/ha).",
                    "recommendation": "Apply nitrogenous fertilizers in split doses (50% basal + 50% tillering/vegetative)."
                })
                n_fert = Fertilizer.objects.filter(nitrogen_percentage__gte=20).first()
                if n_fert:
                    suggested_fertilizers.append({
                        "id": n_fert.id,
                        "fertilizer_name": n_fert.fertilizer_name,
                        "fertilizer_type": n_fert.fertilizer_type,
                        "npk_percentage": f"{n_fert.nitrogen_percentage}:{n_fert.phosphorus_percentage}:{n_fert.potassium_percentage}",
                        "reason": f"Supplies high-analysis nitrogen to correct deficit of {soil_n} kg/ha.",
                        "application_timing": n_fert.application_timing,
                        "application_method": n_fert.application_method,
                        "recommended_dosage": n_fert.dosage_per_hectare if crop_obj else "100-150 kg/ha (split application)",
                        "dosage_validated": bool(crop_obj),
                        "precautions": n_fert.precautions
                    })
            elif soil_n > 560:
                guidelines.append("Soil Nitrogen is HIGH (>560 kg/ha). Reduce chemical N by 25% to prevent lodging and sucking pest buildup.")
            else:
                guidelines.append(f"Soil Nitrogen is MEDIUM ({soil_n} kg/ha). Maintain balanced application.")

        # Evaluate Phosphorus
        if soil_p is not None:
            if soil_p < 10:
                deficiencies.append({
                    "nutrient": "Phosphorus (P)",
                    "status": "Low (<10 kg/ha)",
                    "value": f"{soil_p} kg/ha",
                    "reason": f"Phosphorus is deficient ({soil_p} kg/ha), critical for root development and nodulation.",
                    "recommendation": "Apply phosphatic fertilizer (DAP or SSP) as a basal placement below seed depth."
                })
                p_fert = Fertilizer.objects.filter(phosphorus_percentage__gte=16).first()
                if p_fert and not any(f["id"] == p_fert.id for f in suggested_fertilizers):
                    suggested_fertilizers.append({
                        "id": p_fert.id,
                        "fertilizer_name": p_fert.fertilizer_name,
                        "fertilizer_type": p_fert.fertilizer_type,
                        "npk_percentage": f"{p_fert.nitrogen_percentage}:{p_fert.phosphorus_percentage}:{p_fert.potassium_percentage}",
                        "reason": f"Supplies available P2O5 to overcome low soil level ({soil_p} kg/ha).",
                        "application_timing": p_fert.application_timing,
                        "application_method": p_fert.application_method,
                        "recommended_dosage": p_fert.dosage_per_hectare if crop_obj else "100-125 kg/ha basal placement",
                        "dosage_validated": bool(crop_obj),
                        "precautions": p_fert.precautions
                    })
            elif soil_p > 25:
                guidelines.append(f"Soil Phosphorus is HIGH ({soil_p} kg/ha). Avoid excessive phosphatic fertilizers.")
            else:
                guidelines.append(f"Soil Phosphorus is MEDIUM ({soil_p} kg/ha). Standard basal placement recommended.")

        # Evaluate Potassium
        if soil_k is not None:
            if soil_k < 110:
                deficiencies.append({
                    "nutrient": "Potassium (K)",
                    "status": "Low (<110 kg/ha)",
                    "value": f"{soil_k} kg/ha",
                    "reason": f"Potassium is low ({soil_k} kg/ha), essential for drought tolerance and stem strength.",
                    "recommendation": "Apply Muriate of Potash (MOP 0:0:60) at sowing and flowering stage."
                })
                k_fert = Fertilizer.objects.filter(potassium_percentage__gte=40).first()
                if k_fert and not any(f["id"] == k_fert.id for f in suggested_fertilizers):
                    suggested_fertilizers.append({
                        "id": k_fert.id,
                        "fertilizer_name": k_fert.fertilizer_name,
                        "fertilizer_type": k_fert.fertilizer_type,
                        "npk_percentage": f"{k_fert.nitrogen_percentage}:{k_fert.phosphorus_percentage}:{k_fert.potassium_percentage}",
                        "reason": f"Corrects potassium deficiency ({soil_k} kg/ha) and improves crop stress resistance.",
                        "application_timing": k_fert.application_timing,
                        "application_method": k_fert.application_method,
                        "recommended_dosage": k_fert.dosage_per_hectare if crop_obj else "50-75 kg/ha",
                        "dosage_validated": bool(crop_obj),
                        "precautions": k_fert.precautions
                    })
            else:
                guidelines.append(f"Soil Potassium is adequate ({soil_k} kg/ha). Apply maintenance dose.")

        # Evaluate Organic Carbon
        if soil_oc is not None and soil_oc < 0.50:
            deficiencies.append({
                "nutrient": "Organic Carbon",
                "status": "Low (<0.50%)",
                "value": f"{soil_oc}%",
                "reason": "Low organic carbon reduces microbial activity and nutrient holding capacity.",
                "recommendation": "Incorporate 5-10 tonnes/ha Farmyard Manure (FYM) or 2.5 tonnes/ha Vermicompost."
            })
            org_fert = Fertilizer.objects.filter(fertilizer_type='Organic').first()
            if org_fert and not any(f["id"] == org_fert.id for f in suggested_fertilizers):
                suggested_fertilizers.append({
                    "id": org_fert.id,
                    "fertilizer_name": org_fert.fertilizer_name,
                    "fertilizer_type": org_fert.fertilizer_type,
                    "npk_percentage": f"{org_fert.nitrogen_percentage}:{org_fert.phosphorus_percentage}:{org_fert.potassium_percentage}",
                    "reason": "Enhances soil humus, water holding capacity, and beneficial mycorrhiza.",
                    "application_timing": org_fert.application_timing,
                    "application_method": org_fert.application_method,
                    "recommended_dosage": "2.5 - 5.0 tonnes/ha during land preparation",
                    "dosage_validated": True,
                    "precautions": org_fert.precautions
                })

        # Evaluate Soil pH condition
        if soil_ph is not None:
            if soil_ph < 6.0:
                guidelines.append("Soil is Acidic (pH < 6.0). Apply agricultural lime or dolomite at 200-300 kg/ha to optimize nutrient uptake.")
            elif soil_ph > 8.0:
                guidelines.append("Soil is Moderately Alkaline / Sodic (pH > 8.0). Apply Gypsum at 250-500 kg/ha and incorporate green manure.")

        # Fallback if no deficit
        if not suggested_fertilizers:
            for f in Fertilizer.objects.all()[:3]:
                suggested_fertilizers.append({
                    "id": f.id,
                    "fertilizer_name": f.fertilizer_name,
                    "fertilizer_type": f.fertilizer_type,
                    "npk_percentage": f"{f.nitrogen_percentage}:{f.phosphorus_percentage}:{f.potassium_percentage}",
                    "reason": "Recommended for balanced general nutrient maintenance.",
                    "application_timing": f.application_timing,
                    "application_method": f.application_method,
                    "recommended_dosage": f.dosage_per_hectare,
                    "dosage_validated": False,
                    "precautions": f.precautions
                })

        if not guidelines:
            guidelines.append("Soil nutrient levels appear balanced. Follow university recommended basal dose.")

        requires_field_test = (res_level != "village")

        return Response({
            "success": True,
            "target_crop": crop_name or "General Crop Advisory",
            "crop_specific_nutrients": crop_obj.fertilizer_requirement if crop_obj else "Standard package of practices",
            "location": {
                "state": "Gujarat",
                "district": resolved_district,
                "taluka": resolved_taluka,
                "village": resolved_village,
                "resolution_level": res_level,
                "data_level_notice": data_level_notice,
                "data_source": soil_rec.data_source if soil_rec else "Gujarat Agricultural Extension Standards",
            },
            "soil_test_values": {
                "soil_ph": soil_ph,
                "nitrogen_kg_ha": soil_n,
                "phosphorus_kg_ha": soil_p,
                "potassium_kg_ha": soil_k,
                "organic_carbon_pct": soil_oc,
                "fertility_status": "Balanced" if not deficiencies else "Requires Amendment"
            },
            "requires_field_soil_test": requires_field_test,
            "soil_test_notice": (
                "ખેતર સ્તરે ચોક્કસ ખાતર માત્રા માટે માન્ય સરકારી લેબોરેટરી / KVK માં જમીન પરીક્ષણ (Soil Test) કરાવવું જરૂરી છે."
                if requires_field_test else
                "આ સલાહ ગામ કક્ષાના માટી પરીક્ષણ ડેટા પર આધારિત છે."
            ),
            "deficiencies_detected": deficiencies,
            "advisory_guidelines": guidelines,
            "recommended_fertilizers": suggested_fertilizers,
            "precautions": cautions or [
                "જમીનમાં પૂરતો ભેજ હોય ત્યારે જ રાસાયણિક ખાતર આપો (Apply fertilizers only when soil has adequate moisture).",
                "ખાતર આપ્યા પછી તરત હળવું પિયત આપો (Apply light irrigation after fertilizer application).",
                "ખાતર વાપરતી વખતે મોં પર માસ્ક અને હાથમાં મોજા પહેરો."
            ],
            "disclaimer": (
                "IMPORTANT: Fertilizer recommendations are advisory and based on university Package of Practices. "
                "Exact field dosage depends on crop variety, soil depth, and laboratory soil testing."
            )
        })
