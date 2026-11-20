from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.views import APIView
import math
import requests
from .models import State, District, Taluka, Village
from .serializers import StateSerializer, DistrictSerializer, TalukaSerializer, VillageSerializer


def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def resolve_location_from_coords(lat_f, lon_f):
    """
    Given latitude and longitude, resolves to Gujarat State, District, Taluka, and Village.
    First finds the nearest database entities using Haversine calculation,
    supplemented with reverse-geocoding if available.
    """
    # 1. Check all districts
    districts = District.objects.all().select_related('state')
    best_district = None
    min_dist_district = float('inf')

    for d in districts:
        if d.latitude is not None and d.longitude is not None:
            dist = haversine(lat_f, lon_f, d.latitude, d.longitude)
            if dist < min_dist_district:
                min_dist_district = dist
                best_district = d

    if not best_district:
        best_district = districts.first()
        min_dist_district = 0.0

    if not best_district:
        return None

    # 2. Find best Taluka in this District
    talukas = Taluka.objects.filter(district=best_district)
    best_taluka = None
    min_dist_taluka = float('inf')

    for t in talukas:
        if t.latitude is not None and t.longitude is not None:
            dist = haversine(lat_f, lon_f, t.latitude, t.longitude)
            if dist < min_dist_taluka:
                min_dist_taluka = dist
                best_taluka = t

    if not best_taluka:
        best_taluka = talukas.first()

    # 3. Find best Village in this Taluka
    best_village = None
    if best_taluka:
        villages = Village.objects.filter(taluka=best_taluka)
        min_dist_village = float('inf')
        for v in villages:
            if v.latitude is not None and v.longitude is not None:
                dist = haversine(lat_f, lon_f, v.latitude, v.longitude)
                if dist < min_dist_village:
                    min_dist_village = dist
                    best_village = v
        if not best_village:
            best_village = villages.first()

    # 4. Try optional reverse-geocoding for exact village/taluka name if online
    try:
        headers = {'User-Agent': 'SmartKrushi-AgriAdvisor/1.0'}
        geo_res = requests.get(
            'https://nominatim.openstreetmap.org/reverse',
            params={'lat': lat_f, 'lon': lon_f, 'format': 'json', 'zoom': 14},
            headers=headers,
            timeout=2.0
        )
        if geo_res.status_code == 200:
            addr = geo_res.json().get('address', {})
            detected_district = addr.get('state_district') or addr.get('county')
            detected_subdistrict = addr.get('county') or addr.get('subdistrict') or addr.get('taluk')
            detected_village = addr.get('village') or addr.get('suburb') or addr.get('town') or addr.get('hamlet')

            if detected_district:
                matched_dist = District.objects.filter(district_name__icontains=detected_district.replace(' District', '')).first()
                if matched_dist:
                    best_district = matched_dist
                    if detected_subdistrict:
                        matched_tal = Taluka.objects.filter(district=matched_dist, taluka_name__icontains=detected_subdistrict).first()
                        if matched_tal:
                            best_taluka = matched_tal
                    if detected_village and best_taluka:
                        matched_vil = Village.objects.filter(taluka=best_taluka, village_name__icontains=detected_village).first()
                        if matched_vil:
                            best_village = matched_vil
    except Exception:
        # Fallback to database nearest resolution
        pass

    state_name = best_district.state.state_name if best_district.state else "Gujarat"
    state_id = best_district.state.id if best_district.state else 1
    taluka_name = best_taluka.taluka_name if best_taluka else "Unknown Taluka"
    taluka_id = best_taluka.id if best_taluka else None
    village_name = best_village.village_name if best_village else (taluka_name + " Rural")
    village_id = best_village.id if best_village else None

    state_gu = best_district.state.state_name_gu if (best_district.state and best_district.state.state_name_gu) else "ગુજરાત"
    district_gu = best_district.district_name_gu or best_district.district_name
    taluka_gu = best_taluka.taluka_name_gu if (best_taluka and best_taluka.taluka_name_gu) else taluka_name
    village_gu = best_village.village_name_gu if (best_village and best_village.village_name_gu) else village_name

    formatted_address = f"{village_name}, {taluka_name}, {best_district.district_name}, {state_name}"
    formatted_address_gu = f"{village_gu}, {taluka_gu}, {district_gu}, {state_gu}"

    return {
        "success": True,
        "latitude": lat_f,
        "longitude": lon_f,
        "state": state_name,
        "state_gu": state_gu,
        "state_id": state_id,
        "district": best_district.district_name,
        "district_gu": district_gu,
        "district_id": best_district.id,
        "taluka": taluka_name,
        "taluka_gu": taluka_gu,
        "taluka_id": taluka_id,
        "village": village_name,
        "village_gu": village_gu,
        "village_id": village_id,
        "village_code": best_village.village_code if best_village else None,
        "distance_km": round(min_dist_district, 2),
        "formatted_address": formatted_address,
        "formatted_address_gu": formatted_address_gu
    }


class LocationDetectView(APIView):
    """
    GET /api/location/detect/?latitude=&longitude=
    Detect user's current location and reverse-geocode to State, District, Taluka, and Village in Gujarat.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        lat = request.query_params.get('latitude') or request.query_params.get('lat')
        lon = request.query_params.get('longitude') or request.query_params.get('lon')

        if lat is None or lon is None:
            return Response(
                {"error": "Query parameters 'latitude' and 'longitude' are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            lat_f = float(lat)
            lon_f = float(lon)
        except (ValueError, TypeError):
            return Response(
                {"error": "Latitude and longitude must be valid floating numbers."},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = resolve_location_from_coords(lat_f, lon_f)
        if not result:
            return Response({"error": "No matching Gujarat location found in database."}, status=status.HTTP_404_NOT_FOUND)

        return Response(result)

    def post(self, request):
        lat = request.data.get('latitude') or request.data.get('lat')
        lon = request.data.get('longitude') or request.data.get('lon')

        if lat is None or lon is None:
            return Response(
                {"error": "Fields 'latitude' and 'longitude' are required in request body."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            lat_f = float(lat)
            lon_f = float(lon)
        except (ValueError, TypeError):
            return Response(
                {"error": "Latitude and longitude must be valid floating numbers."},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = resolve_location_from_coords(lat_f, lon_f)
        if not result:
            return Response({"error": "No matching Gujarat location found in database."}, status=status.HTTP_404_NOT_FOUND)

        return Response(result)


class LocationHierarchyView(APIView):
    """
    GET /api/location/hierarchy/
    Returns the complete hierarchical structure of Gujarat:
    Districts -> Talukas -> Villages.
    Allows manual location selection dropdowns.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        district_id = request.query_params.get('district_id')
        district_name = request.query_params.get('district') or request.query_params.get('district_name')

        districts_qs = District.objects.all().select_related('state').prefetch_related('talukas__villages')
        if district_id:
            districts_qs = districts_qs.filter(id=district_id)
        elif district_name:
            districts_qs = districts_qs.filter(district_name__icontains=district_name)

        hierarchy = []
        for d in districts_qs:
            taluka_list = []
            for t in d.talukas.all():
                village_list = [
                    {
                        "id": v.id,
                        "name": v.village_name,
                        "village_name": v.village_name,
                        "name_gu": v.village_name_gu or v.village_name,
                        "village_name_gu": v.village_name_gu or v.village_name,
                        "village_code": v.village_code,
                        "latitude": v.latitude,
                        "longitude": v.longitude,
                    }
                    for v in t.villages.all()
                ]
                taluka_list.append({
                    "id": t.id,
                    "name": t.taluka_name,
                    "taluka_name": t.taluka_name,
                    "name_gu": t.taluka_name_gu or t.taluka_name,
                    "taluka_name_gu": t.taluka_name_gu or t.taluka_name,
                    "taluka_code": t.taluka_code,
                    "latitude": t.latitude,
                    "longitude": t.longitude,
                    "villages": village_list,
                    "village_count": len(village_list)
                })

            hierarchy.append({
                "id": d.id,
                "name": d.district_name,
                "district_name": d.district_name,
                "name_gu": d.district_name_gu or d.district_name,
                "district_name_gu": d.district_name_gu or d.district_name,
                "district_code": d.district_code,
                "state": d.state.state_name if d.state else "Gujarat",
                "state_gu": d.state.state_name_gu if d.state else "ગુજરાત",
                "state_id": d.state.id if d.state else 1,
                "latitude": d.latitude,
                "longitude": d.longitude,
                "talukas": taluka_list,
                "taluka_count": len(taluka_list)
            })

        return Response({
            "state": "Gujarat",
            "state_gu": "ગુજરાત",
            "total_districts": len(hierarchy),
            "districts": hierarchy
        })


class StateViewSet(viewsets.ModelViewSet):
    queryset = State.objects.all().prefetch_related('districts')
    serializer_class = StateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['state_name', 'state_name_gu', 'state_code']
    ordering_fields = ['state_name', 'created_at']


class DistrictViewSet(viewsets.ModelViewSet):
    queryset = District.objects.all().select_related('state').prefetch_related('talukas')
    serializer_class = DistrictSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['district_name', 'district_name_gu', 'district_code', 'state__state_name', 'state__state_name_gu']
    ordering_fields = ['district_name', 'created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        state_id = self.request.query_params.get('state_id') or self.request.query_params.get('state')
        state_name = self.request.query_params.get('state_name')

        if state_id:
            if state_id.isdigit():
                qs = qs.filter(state_id=state_id)
            else:
                qs = qs.filter(state__state_name__iexact=state_id)
        if state_name:
            qs = qs.filter(state__state_name__icontains=state_name)
        return qs

    @action(detail=False, methods=['get', 'post'], url_path='locate')
    def locate(self, request):
        """
        Resolve device GPS coordinates to nearest district and state.
        """
        lat = (
            request.query_params.get('latitude') or
            request.query_params.get('lat') or
            (request.data.get('latitude') if isinstance(request.data, dict) else None)
        )
        lon = (
            request.query_params.get('longitude') or
            request.query_params.get('lon') or
            (request.data.get('longitude') if isinstance(request.data, dict) else None)
        )

        if lat is None or lon is None:
            return Response(
                {"error": "Latitude and longitude are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            lat_f = float(lat)
            lon_f = float(lon)
        except (ValueError, TypeError):
            return Response(
                {"error": "Latitude and longitude must be valid floating numbers."},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = resolve_location_from_coords(lat_f, lon_f)
        if not result:
            return Response({"error": "No district found in database."}, status=status.HTTP_404_NOT_FOUND)

        return Response(result)


class TalukaViewSet(viewsets.ModelViewSet):
    queryset = Taluka.objects.all().select_related('district', 'district__state').prefetch_related('villages')
    serializer_class = TalukaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['taluka_name', 'taluka_name_gu', 'taluka_code', 'district__district_name', 'district__district_name_gu']
    ordering_fields = ['taluka_name', 'created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        district_id = self.request.query_params.get('district_id') or self.request.query_params.get('district')
        district_name = self.request.query_params.get('district_name')
        state_name = self.request.query_params.get('state_name')

        if district_id:
            if district_id.isdigit():
                qs = qs.filter(district_id=district_id)
            else:
                qs = qs.filter(district__district_name__iexact=district_id)
        if district_name:
            qs = qs.filter(district__district_name__icontains=district_name)
        if state_name:
            qs = qs.filter(district__state__state_name__icontains=state_name)
        return qs


class VillageViewSet(viewsets.ModelViewSet):
    queryset = Village.objects.all().select_related('taluka', 'taluka__district', 'taluka__district__state')
    serializer_class = VillageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        'village_name', 'village_name_gu', 'village_code',
        'taluka__taluka_name', 'taluka__taluka_name_gu',
        'taluka__district__district_name', 'taluka__district__district_name_gu'
    ]
    ordering_fields = ['village_name', 'created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        taluka_id = self.request.query_params.get('taluka_id') or self.request.query_params.get('taluka')
        taluka_name = self.request.query_params.get('taluka_name')
        district_id = self.request.query_params.get('district_id')
        district_name = self.request.query_params.get('district_name') or self.request.query_params.get('district')

        if taluka_id:
            if taluka_id.isdigit():
                qs = qs.filter(taluka_id=taluka_id)
            else:
                qs = qs.filter(taluka__taluka_name__iexact=taluka_id)
        if taluka_name:
            qs = qs.filter(taluka__taluka_name__icontains=taluka_name)
        if district_id:
            if district_id.isdigit():
                qs = qs.filter(taluka__district_id=district_id)
            else:
                qs = qs.filter(taluka__district__district_name__iexact=district_id)
        if district_name:
            qs = qs.filter(taluka__district__district_name__icontains=district_name)
        return qs


class LocationBulkImportView(APIView):
    """
    POST /api/location/bulk-import/
    Import locations from CSV or Excel file.
    Expected columns:
    state, state_gu, state_code, district, district_gu, district_code,
    taluka, taluka_gu, taluka_code, village, village_gu, village_code, latitude, longitude
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request):
        import csv
        import io

        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response(
                {"error": "A 'file' (.csv or .xlsx) must be provided in multipart request."},
                status=status.HTTP_400_BAD_REQUEST
            )

        filename = file_obj.name.lower()
        rows = []
        if filename.endswith('.csv'):
            decoded_file = file_obj.read().decode('utf-8-sig', errors='replace')
            reader = csv.DictReader(io.StringIO(decoded_file))
            rows = list(reader)
        elif filename.endswith(('.xls', '.xlsx')):
            try:
                import pandas as pd
                df = pd.read_excel(file_obj)
                df = df.where(pd.notnull(df), None)
                rows = df.to_dict(orient='records')
            except ImportError:
                return Response(
                    {"error": "pandas and openpyxl are required to process Excel files."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            return Response(
                {"error": "Unsupported file format. Please upload a .csv or .xlsx file."},
                status=status.HTTP_400_BAD_REQUEST
            )

        created_states = 0
        created_districts = 0
        created_talukas = 0
        created_villages = 0
        errors = []

        for idx, row in enumerate(rows, start=1):
            try:
                state_name = str(row.get('state') or 'Gujarat').strip()
                state_gu = str(row.get('state_gu') or 'ગુજરાત').strip()
                state_code = str(row.get('state_code') or '').strip() or None

                state_obj, s_created = State.objects.get_or_create(
                    state_name=state_name,
                    defaults={'state_name_gu': state_gu, 'state_code': state_code}
                )
                if s_created:
                    created_states += 1

                dist_name = str(row.get('district') or '').strip()
                if not dist_name:
                    continue
                dist_gu = str(row.get('district_gu') or '').strip() or None
                dist_code = str(row.get('district_code') or '').strip() or None
                dist_lat = float(row.get('district_lat') or row.get('latitude') or 0.0) or None
                dist_lon = float(row.get('district_lon') or row.get('longitude') or 0.0) or None

                dist_obj, d_created = District.objects.get_or_create(
                    state=state_obj,
                    district_name=dist_name,
                    defaults={
                        'district_name_gu': dist_gu,
                        'district_code': dist_code,
                        'latitude': dist_lat,
                        'longitude': dist_lon
                    }
                )
                if d_created:
                    created_districts += 1
                elif dist_gu and not dist_obj.district_name_gu:
                    dist_obj.district_name_gu = dist_gu
                    dist_obj.save(update_fields=['district_name_gu'])

                tal_name = str(row.get('taluka') or '').strip()
                if not tal_name:
                    continue
                tal_gu = str(row.get('taluka_gu') or '').strip() or None
                tal_code = str(row.get('taluka_code') or '').strip() or None

                tal_obj, t_created = Taluka.objects.get_or_create(
                    district=dist_obj,
                    taluka_name=tal_name,
                    defaults={'taluka_name_gu': tal_gu, 'taluka_code': tal_code}
                )
                if t_created:
                    created_talukas += 1
                elif tal_gu and not tal_obj.taluka_name_gu:
                    tal_obj.taluka_name_gu = tal_gu
                    tal_obj.save(update_fields=['taluka_name_gu'])

                vil_name = str(row.get('village') or '').strip()
                if not vil_name:
                    continue
                vil_gu = str(row.get('village_gu') or '').strip() or None
                vil_code = str(row.get('village_code') or '').strip() or None
                vil_lat = float(row.get('latitude') or 0.0) or None
                vil_lon = float(row.get('longitude') or 0.0) or None

                vil_obj, v_created = Village.objects.get_or_create(
                    taluka=tal_obj,
                    village_name=vil_name,
                    defaults={
                        'village_name_gu': vil_gu,
                        'village_code': vil_code,
                        'latitude': vil_lat,
                        'longitude': vil_lon
                    }
                )
                if v_created:
                    created_villages += 1
            except Exception as e:
                errors.append(f"Row {idx}: {str(e)}")

        return Response({
            "message": "Bulk import completed.",
            "total_rows_processed": len(rows),
            "created_states": created_states,
            "created_districts": created_districts,
            "created_talukas": created_talukas,
            "created_villages": created_villages,
            "errors_count": len(errors),
            "errors": errors[:20]
        })
