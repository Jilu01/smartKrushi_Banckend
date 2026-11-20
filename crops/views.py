from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db.models import Avg, Sum, Max, Min, Count, Q
from .models import Crop, CropRecord, CropData
from .serializers import CropSerializer, CropRecordSerializer, CropDataSerializer


class CropViewSet(viewsets.ModelViewSet):
    queryset = Crop.objects.all()
    serializer_class = CropSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['crop_name', 'scientific_name', 'crop_category', 'suitable_soil', 'growing_season']
    ordering_fields = ['crop_name', 'crop_duration_days', 'suitable_ph_min', 'created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        category = self.request.query_params.get('category')
        season = self.request.query_params.get('season')
        soil = self.request.query_params.get('soil')
        water = self.request.query_params.get('water')

        if category:
            qs = qs.filter(crop_category__icontains=category)
        if season:
            qs = qs.filter(growing_season__icontains=season)
        if soil:
            qs = qs.filter(suitable_soil__icontains=soil)
        if water:
            qs = qs.filter(water_requirement__iexact=water)
        return qs

    @action(detail=False, methods=['get'], url_path='categories')
    def categories(self, request):
        """
        List crop categories with counts and multilingual names.
        """
        from .serializers import CATEGORY_TRANSLATIONS
        categories_counts = dict(
            Crop.objects.values('crop_category').annotate(count=Count('id')).values_list('crop_category', 'count')
        )
        
        all_choices = [c[0] for c in Crop.CATEGORY_CHOICES]
        result = []
        for cat in all_choices:
            count = categories_counts.get(cat, 0)
            key = cat.lower()
            trans = CATEGORY_TRANSLATIONS.get(key, {})
            result.append({
                "id": key.replace(" ", "_"),
                "name": cat,
                "name_gu": trans.get('gu', cat),
                "name_hi": trans.get('hi', cat),
                "name_en": trans.get('en', cat),
                "crop_count": count
            })
        return Response({
            "total_categories": len(result),
            "categories": result
        })

    @action(detail=False, methods=['get'], url_path='by-season')
    def by_season(self, request):
        season = request.query_params.get('season')
        if not season:
            return Response(
                {"error": "Please provide a 'season' query parameter (e.g. Kharif, Rabi, Zaid, Annual)."},
                status=status.HTTP_400_BAD_REQUEST
            )
        qs = self.get_queryset().filter(growing_season__icontains=season)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(self.get_serializer(qs, many=True).data)

    @action(detail=False, methods=['get'], url_path='suitable-for-soil')
    def suitable_for_soil(self, request):
        soil_type = request.query_params.get('soil_type') or request.query_params.get('soil')
        soil_ph_str = request.query_params.get('soil_ph') or request.query_params.get('ph')

        qs = self.get_queryset()

        if soil_type:
            qs = qs.filter(suitable_soil__icontains=soil_type)

        if soil_ph_str:
            try:
                soil_ph = float(soil_ph_str)
                # Crop is suitable if ph is between min and max (with slight 0.3 tolerance)
                qs = qs.filter(
                    suitable_ph_min__lte=soil_ph + 0.3,
                    suitable_ph_max__gte=soil_ph - 0.3
                )
            except ValueError:
                return Response({"error": "Invalid soil_ph parameter. Must be a float."}, status=status.HTTP_400_BAD_REQUEST)

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(self.get_serializer(qs, many=True).data)

    @action(detail=False, methods=['get'], url_path='by-location')
    def by_location(self, request):
        state = request.query_params.get('state')
        district = request.query_params.get('district')
        taluka = request.query_params.get('taluka')

        if not (state or district):
            return Response(
                {"error": "Please provide 'state' and/or 'district' parameter."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Find distinct crops from CropRecord for this location
        records = CropRecord.objects.all()
        if state:
            records = records.filter(state__icontains=state)
        if district:
            records = records.filter(district__icontains=district)
        if taluka:
            records = records.filter(taluka__icontains=taluka)

        crop_names = records.values_list('crop_name', flat=True).distinct()

        # Also check legacy CropData table
        legacy_records = CropData.objects.all()
        if state:
            legacy_records = legacy_records.filter(state__icontains=state)
        if district:
            legacy_records = legacy_records.filter(district__icontains=district)
        legacy_names = legacy_records.values_list('crop_name', flat=True).distinct()

        combined_names = set(crop_names).union(set(legacy_names))

        crops = Crop.objects.filter(crop_name__in=combined_names)
        return Response({
            "location": {"state": state, "district": district, "taluka": taluka},
            "total_crops_found": len(combined_names),
            "crop_names": sorted(list(combined_names)),
            "crop_profiles": CropSerializer(crops, many=True).data
        })

    @action(detail=False, methods=['get'], url_path='recommendations')
    def recommendations(self, request):
        """
        GET /api/crops/recommendations/?location_id=&village_id=&taluka_id=&district_id=&district=&season=
        Dynamic crop recommendations evaluating:
        - Soil type, pH, NPK, organic carbon
        - Live weather (temp, rainfall, humidity)
        - Season (Kharif, Rabi, Zaid, Annual)
        - Crop agronomic requirements
        Returns suitability score (0-100) with defined calculation methodology and reasons.
        """
        from datetime import datetime
        from soil.views import resolve_hierarchical_soil
        from weather.services import WeatherService
        from locations.models import District as LocDistrict, Taluka as LocTaluka, Village as LocVillage

        village_id = request.query_params.get('village_id')
        taluka_id = request.query_params.get('taluka_id')
        district_id = request.query_params.get('district_id') or request.query_params.get('location_id')
        village = request.query_params.get('village') or request.query_params.get('village_name')
        taluka = request.query_params.get('taluka') or request.query_params.get('taluka_name')
        district = request.query_params.get('district') or request.query_params.get('district_name')
        lat = request.query_params.get('latitude') or request.query_params.get('lat')
        lon = request.query_params.get('longitude') or request.query_params.get('lon')
        target_season = request.query_params.get('season') or request.query_params.get('growing_season')

        # 1. Resolve Soil Data using the hierarchical lookup
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

        soil_record = soil_res["record"]
        res_level = soil_res["resolution_level"]
        data_level_notice = soil_res["data_level_notice"]
        resolved_district = soil_res["target_district"]
        resolved_taluka = soil_res["target_taluka"]
        resolved_village = soil_res["target_village"]

        # Default fallback values if no soil record exists
        soil_type = soil_record.soil_type if soil_record else "Medium Black"
        soil_ph = soil_record.soil_ph if soil_record else 7.2
        nitrogen = soil_record.nitrogen if soil_record else 240.0
        phosphorus = soil_record.phosphorus if soil_record else 14.0
        potassium = soil_record.potassium if soil_record else 280.0
        organic_carbon = soil_record.organic_carbon if soil_record else 0.50

        # 2. Resolve coordinates and fetch live weather
        lat_f = float(lat) if lat else None
        lon_f = float(lon) if lon else None
        if (lat_f is None or lon_f is None) and resolved_district:
            d_entry = LocDistrict.objects.filter(district_name__icontains=resolved_district).first()
            if d_entry and d_entry.latitude and d_entry.longitude:
                lat_f = d_entry.latitude
                lon_f = d_entry.longitude

        weather_data = {}
        if lat_f is not None and lon_f is not None:
            w_res = WeatherService.fetch_live_weather(
                latitude=lat_f,
                longitude=lon_f,
                district=resolved_district or "Gujarat"
            )
            if w_res.get("success"):
                weather_data = w_res.get("data", {})

        current_temp = weather_data.get("temperature", 28.0)
        current_rain = weather_data.get("rainfall", 0.0)
        current_humidity = weather_data.get("humidity", 50.0)

        # 3. Determine Agricultural Season if not provided
        if not target_season:
            month = datetime.now().month
            if 6 <= month <= 10:
                target_season = "Kharif"
            elif month in [11, 12, 1, 2]:
                target_season = "Rabi"
            else:
                target_season = "Zaid"

        # 4. Evaluate each crop against soil, weather, season, and requirements
        candidates = []
        for crop in Crop.objects.all():
            score = 0
            reasons = []

            # Factor A: Soil Type & Texture Match (Max 25 pts)
            st_clean = (crop.suitable_soil or "").lower()
            if soil_type.lower() in st_clean:
                score += 25
                reasons.append(f"Thrives in {soil_type} soil of {resolved_district}")
            elif any(t in st_clean for t in ["black", "alluvial", "loam"]):
                score += 15
                reasons.append(f"Compatible with {soil_type} soil structure")
            else:
                score += 8

            # Factor B: Soil pH Compatibility (Max 20 pts)
            ph_min = crop.suitable_ph_min or 6.0
            ph_max = crop.suitable_ph_max or 8.0
            if ph_min <= soil_ph <= ph_max:
                score += 20
                reasons.append(f"Soil pH {soil_ph} is within optimal range ({ph_min} - {ph_max})")
            elif abs(soil_ph - ph_min) <= 0.6 or abs(soil_ph - ph_max) <= 0.6:
                score += 10
                reasons.append(f"Soil pH {soil_ph} is acceptable with minor conditioning")
            else:
                score += 2

            # Factor C: Nutrient Requirement Compatibility (Max 20 pts)
            is_legume = "pulse" in (crop.crop_category or "").lower() or crop.crop_name.lower() in ["groundnut", "chickpea", "gram", "moong"]
            if is_legume:
                score += 20
                reasons.append("Fixes atmospheric nitrogen, ideal for local soil rejuvenation")
            elif nitrogen >= 280 and phosphorus >= 12:
                score += 18
                reasons.append(f"Soil fertility (N: {nitrogen} kg/ha, P: {phosphorus} kg/ha) supports high yield")
            elif nitrogen < 240:
                score += 12
                reasons.append("Moderate feeder suitable with recommended basal fertilizer")
            else:
                score += 15

            # Factor D: Temperature and Climate Match (Max 20 pts)
            t_min = crop.temperature_min or 15.0
            t_max = crop.temperature_max or 36.0
            if t_min <= current_temp <= t_max:
                score += 20
                reasons.append(f"Current temperature {current_temp}°C is within optimal tolerance ({t_min}°C - {t_max}°C)")
            elif abs(current_temp - t_min) <= 4 or abs(current_temp - t_max) <= 4:
                score += 12
            else:
                score += 5

            # Factor E: Season Compatibility (Max 15 pts)
            c_season = (crop.growing_season or "").lower()
            if target_season.lower() in c_season or c_season in ["annual", "perennial"]:
                score += 15
                reasons.append(f"Matches current {target_season} cropping season in Gujarat")
            else:
                score += 0

            # Determine suitability rating
            if score >= 80:
                rating = "Highly Suitable"
            elif score >= 60:
                rating = "Moderately Suitable"
            else:
                rating = "Marginally Suitable"

            candidates.append({
                "id": crop.id,
                "crop_name": crop.crop_name,
                "scientific_name": crop.scientific_name,
                "crop_category": crop.crop_category,
                "crop_description": crop.crop_description,
                "growing_season": crop.growing_season,
                "crop_duration_days": crop.crop_duration_days,
                "suitable_soil": crop.suitable_soil,
                "required_ph_range": f"{ph_min} - {ph_max}",
                "temperature_requirement": f"{t_min}°C - {t_max}°C",
                "water_requirement": crop.water_requirement,
                "rainfall_requirement": crop.rainfall_requirement,
                "sowing_period": crop.sowing_period,
                "harvesting_period": crop.harvesting_period,
                "irrigation_method": crop.irrigation_method,
                "common_diseases": crop.common_diseases,
                "fertilizer_requirement": crop.fertilizer_requirement,
                "suitability_score": min(score, 100),
                "suitability_rating": rating,
                "reasons": reasons,
            })

        candidates.sort(key=lambda x: x["suitability_score"], reverse=True)

        return Response({
            "success": True,
            "season": target_season,
            "location": {
                "state": "Gujarat",
                "district": resolved_district,
                "taluka": resolved_taluka,
                "village": resolved_village,
                "resolution_level": res_level,
                "data_level_notice": data_level_notice,
                "data_source": soil_record.data_source if soil_record else "Regional Agrometeorology",
                "latitude": lat_f,
                "longitude": lon_f
            },
            "environmental_conditions": {
                "soil_type": soil_type,
                "soil_ph": soil_ph,
                "nitrogen_kg_ha": nitrogen,
                "phosphorus_kg_ha": phosphorus,
                "potassium_kg_ha": potassium,
                "current_temperature_c": current_temp,
                "current_rainfall_mm": current_rain,
                "current_humidity_pct": current_humidity,
            },
            "scoring_methodology": {
                "soil_type_weight": "25%",
                "soil_ph_weight": "20%",
                "nutrient_fertility_weight": "20%",
                "temperature_climate_weight": "20%",
                "season_match_weight": "15%",
                "max_score": 100
            },
            "total_recommended_crops": len(candidates),
            "recommendations": candidates
        })

    @action(detail=False, methods=['get', 'post'], url_path='recommend')
    def recommend(self, request):
        """
        Complete AI Crop & Profit Recommendation Pipeline
        POST /api/v1/crops/recommend/ or GET /api/v1/crops/recommend/
        """
        from recommendations.ai_engine import ComprehensiveAgriEngine
        from recommendations.models import CropRecommendation
        params = request.data if request.method == 'POST' else request.query_params

        district = params.get('district') or 'Ahmedabad'
        taluka = params.get('taluka')
        village = params.get('village')
        state = params.get('state') or 'Gujarat'

        def to_float(val):
            try:
                return float(val) if val is not None and val != '' else None
            except (ValueError, TypeError):
                return None

        latitude = to_float(params.get('latitude') or params.get('lat'))
        longitude = to_float(params.get('longitude') or params.get('lon'))
        soil_type = params.get('soil_type')
        soil_ph = to_float(params.get('soil_ph') or params.get('ph'))
        nitrogen = to_float(params.get('nitrogen') or params.get('n'))
        phosphorus = to_float(params.get('phosphorus') or params.get('p'))
        potassium = to_float(params.get('potassium') or params.get('k'))
        organic_carbon = to_float(params.get('organic_carbon') or params.get('oc'))
        soil_moisture = to_float(params.get('soil_moisture'))
        land_area_ha = to_float(params.get('land_area') or params.get('land_area_ha') or params.get('area')) or 1.0
        irrigation_type = params.get('irrigation_type') or params.get('irrigation') or 'Borewell'
        target_season = params.get('season') or params.get('growing_season')

        result = ComprehensiveAgriEngine.recommend(
            district=district,
            taluka=taluka,
            village=village,
            state=state,
            latitude=latitude,
            longitude=longitude,
            soil_type=soil_type,
            soil_ph=soil_ph,
            nitrogen=nitrogen,
            phosphorus=phosphorus,
            potassium=potassium,
            organic_carbon=organic_carbon,
            soil_moisture=soil_moisture,
            land_area_ha=land_area_ha,
            irrigation_type=irrigation_type,
            target_season=target_season
        )

        # Log session in database
        try:
            CropRecommendation.objects.create(
                session_id=result.get("session_id", "rec_default"),
                district=district,
                taluka=taluka or "",
                village=village or "",
                season=result.get("environment_snapshot", {}).get("season", "Kharif"),
                land_area_ha=land_area_ha,
                top_recommended_crops=result.get("top_recommended_crops", []),
                weather_summary=result.get("environment_snapshot", {}),
                soil_summary={
                    "soil_type": soil_type,
                    "soil_ph": soil_ph,
                    "nitrogen": nitrogen,
                    "phosphorus": phosphorus,
                    "potassium": potassium,
                },
                data_provenance={
                    "resolution": result.get("location", {}).get("resolution_level"),
                    "source": "ComprehensiveAgriEngine"
                }
            )
        except Exception as e:
            # Non-blocking log failure
            pass

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='profit-analysis')
    def profit_analysis(self, request):
        """
        GET /api/v1/crops/profit-analysis/?district=Ahmedabad&crop_id=...&land_area=2
        """
        from recommendations.ai_engine import ComprehensiveAgriEngine
        crop_id = request.query_params.get('crop_id')
        district = request.query_params.get('district', 'Ahmedabad')
        land_area = float(request.query_params.get('land_area', 1.0))

        result = ComprehensiveAgriEngine.recommend(
            district=district,
            land_area_ha=land_area
        )
        crops = result.get('top_recommended_crops', [])
        if crop_id:
            crops = [c for c in crops if str(c.get('crop_id')) == str(crop_id)]

        target = crops[0] if crops else (result.get('top_recommended_crops', [{}])[0])
        return Response({
            "success": True,
            "crop_name": target.get("crop_name"),
            "crop_name_gujarati": target.get("crop_name_gujarati"),
            "district": district,
            "land_area_ha": land_area,
            "land_area_acres": round(land_area * 2.47105, 2),
            "expected_yield_kg_per_ha": target.get("expected_yield_kg_per_ha"),
            "total_production_quintals": target.get("total_production_quintals"),
            "selling_price_per_quintal": target.get("expected_selling_price_per_quintal"),
            "estimated_cultivation_cost_per_ha": target.get("estimated_cultivation_cost_per_ha"),
            "estimated_total_cost": target.get("estimated_total_cost"),
            "expected_revenue": target.get("expected_revenue"),
            "expected_net_profit": target.get("expected_net_profit"),
            "profit_per_hectare": target.get("profit_per_hectare"),
            "profit_per_acre": target.get("profit_per_acre"),
            "roi_percentage": target.get("roi_percentage"),
            "break_even_price_per_quintal": target.get("break_even_price_per_quintal"),
            "financial_scenarios": target.get("financial_scenarios"),
            "data_provenance": target.get("data_provenance"),
            "disclaimer": "Figures are estimated projections based on prevailing APMC rates and CACP cultivation baselines."
        })

    @action(detail=False, methods=['get'], url_path='recommendations/history')
    def recommendations_history(self, request):
        from recommendations.models import CropRecommendation
        district = request.query_params.get('district')
        qs = CropRecommendation.objects.all()
        if district:
            qs = qs.filter(district__icontains=district)
        items = qs[:20]
        data = [
            {
                "id": rec.id,
                "session_id": rec.session_id,
                "district": rec.district,
                "taluka": rec.taluka,
                "village": rec.village,
                "season": rec.season,
                "land_area_ha": rec.land_area_ha,
                "created_at": rec.created_at,
                "top_crop": rec.top_recommended_crops[0].get("crop_name") if rec.top_recommended_crops else None,
                "top_profit": rec.top_recommended_crops[0].get("expected_net_profit") if rec.top_recommended_crops else None,
                "top_recommended_crops": rec.top_recommended_crops,
            }
            for rec in items
        ]
        return Response({
            "total_records": len(data),
            "results": data
        })


class CropSeasonCalendarViewSet(viewsets.ModelViewSet):
    from .models import CropSeasonCalendar
    from .serializers import CropSeasonCalendarSerializer
    queryset = CropSeasonCalendar.objects.all().select_related('crop')
    serializer_class = CropSeasonCalendarSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['crop__crop_name', 'state', 'district', 'season']
    ordering_fields = ['district', 'season', 'crop_duration_days']

    def get_queryset(self):
        from .models import CropSeasonCalendar
        qs = CropSeasonCalendar.objects.all().select_related('crop')
        district = self.request.query_params.get('district')
        season = self.request.query_params.get('season')
        crop_id = self.request.query_params.get('crop_id')

        if district:
            qs = qs.filter(district__icontains=district)
        if season:
            qs = qs.filter(season__icontains=season)
        if crop_id:
            qs = qs.filter(crop_id=crop_id)
        return qs


class CropProductionHistoryViewSet(viewsets.ModelViewSet):
    from .models import CropProductionHistory
    from .serializers import CropProductionHistorySerializer
    queryset = CropProductionHistory.objects.all().select_related('crop')
    serializer_class = CropProductionHistorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['crop_name', 'district', 'state', 'season']
    ordering_fields = ['year', 'production_tonnes', 'yield_kg_per_hectare', 'cultivated_area_hectares']

    def get_queryset(self):
        from .models import CropProductionHistory
        qs = CropProductionHistory.objects.all().select_related('crop')
        district = self.request.query_params.get('district')
        crop_id = self.request.query_params.get('crop_id')
        crop_name = self.request.query_params.get('crop') or self.request.query_params.get('crop_name')
        year = self.request.query_params.get('year')

        if district:
            qs = qs.filter(district__icontains=district)
        if crop_id:
            qs = qs.filter(crop_id=crop_id)
        if crop_name:
            qs = qs.filter(crop_name__icontains=crop_name)
        if year:
            qs = qs.filter(year=year)
        return qs


class CropCostViewSet(viewsets.ModelViewSet):
    from .models import CropCost
    from .serializers import CropCostSerializer
    queryset = CropCost.objects.all().select_related('crop')
    serializer_class = CropCostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['crop__crop_name', 'district', 'state']
    ordering_fields = ['total_cultivation_cost', 'year']

    def get_queryset(self):
        from .models import CropCost
        qs = CropCost.objects.all().select_related('crop')
        district = self.request.query_params.get('district')
        crop_id = self.request.query_params.get('crop_id')
        if district:
            qs = qs.filter(district__icontains=district)
        if crop_id:
            qs = qs.filter(crop_id=crop_id)
        return qs


class CropMarketPriceViewSet(viewsets.ModelViewSet):
    from .models import CropMarketPrice
    from .serializers import CropMarketPriceSerializer
    queryset = CropMarketPrice.objects.all().select_related('crop')
    serializer_class = CropMarketPriceSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['crop_name', 'apmc_market', 'district', 'state']
    ordering_fields = ['date', 'modal_price', 'max_price']

    def get_queryset(self):
        from .models import CropMarketPrice
        qs = CropMarketPrice.objects.all().select_related('crop')
        crop = self.request.query_params.get('crop') or self.request.query_params.get('crop_name')
        district = self.request.query_params.get('district')
        apmc = self.request.query_params.get('apmc') or self.request.query_params.get('mandi')
        if crop:
            qs = qs.filter(crop_name__icontains=crop)
        if district:
            qs = qs.filter(district__icontains=district)
        if apmc:
            qs = qs.filter(apmc_market__icontains=apmc)
        return qs


class CropRecordViewSet(viewsets.ModelViewSet):
    queryset = CropRecord.objects.all().select_related('crop')
    serializer_class = CropRecordSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['state', 'district', 'taluka', 'crop_name', 'growing_season']
    ordering_fields = ['year', 'production_tonnes', 'yield_kg_per_hectare', 'area_hectares']

    def get_queryset(self):
        qs = super().get_queryset()
        state = self.request.query_params.get('state')
        district = self.request.query_params.get('district')
        crop_name = self.request.query_params.get('crop') or self.request.query_params.get('crop_name')
        season = self.request.query_params.get('season')
        year = self.request.query_params.get('year')

        if state:
            qs = qs.filter(state__icontains=state)
        if district:
            qs = qs.filter(district__icontains=district)
        if crop_name:
            qs = qs.filter(crop_name__icontains=crop_name)
        if season:
            qs = qs.filter(growing_season__icontains=season)
        if year:
            qs = qs.filter(year=year)
        return qs


class CropCategoryViewSet(viewsets.ModelViewSet):
    from .models import CropCategory
    from .serializers import CropCategorySerializer
    queryset = CropCategory.objects.all()
    serializer_class = CropCategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['category_name', 'category_name_gujarati', 'category_code']
    ordering_fields = ['display_order', 'category_name']


class CropLocationSuitabilityViewSet(viewsets.ModelViewSet):
    from .models import CropLocationSuitability
    from .serializers import CropLocationSuitabilitySerializer
    queryset = CropLocationSuitability.objects.all().select_related('crop')
    serializer_class = CropLocationSuitabilitySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['crop__crop_name', 'district', 'taluka', 'suitability_level']
    ordering_fields = ['suitability_score', 'district']

    def get_queryset(self):
        from .models import CropLocationSuitability
        qs = CropLocationSuitability.objects.all().select_related('crop')
        district = self.request.query_params.get('district')
        crop_id = self.request.query_params.get('crop_id')
        suitability = self.request.query_params.get('suitability')
        season = self.request.query_params.get('season')
        if district:
            qs = qs.filter(district__icontains=district)
        if crop_id:
            qs = qs.filter(crop_id=crop_id)
        if suitability:
            qs = qs.filter(suitability_level__icontains=suitability)
        if season:
            qs = qs.filter(favorable_seasons__icontains=season)
        return qs
