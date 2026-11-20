from rest_framework import serializers
from .models import State, District, Taluka, Village


class VillageSerializer(serializers.ModelSerializer):
    taluka_name = serializers.ReadOnlyField(source='taluka.taluka_name')
    taluka_name_gu = serializers.ReadOnlyField(source='taluka.taluka_name_gu')
    district_name = serializers.ReadOnlyField(source='taluka.district.district_name')
    district_name_gu = serializers.ReadOnlyField(source='taluka.district.district_name_gu')
    state_name = serializers.ReadOnlyField(source='taluka.district.state.state_name')

    class Meta:
        model = Village
        fields = [
            'id', 'taluka', 'taluka_name', 'taluka_name_gu', 'district_name', 'district_name_gu', 'state_name',
            'village_name', 'village_name_gu', 'village_code', 'latitude', 'longitude', 'created_at', 'updated_at'
        ]


class TalukaSerializer(serializers.ModelSerializer):
    district_name = serializers.ReadOnlyField(source='district.district_name')
    district_name_gu = serializers.ReadOnlyField(source='district.district_name_gu')
    state_name = serializers.ReadOnlyField(source='district.state.state_name')
    village_count = serializers.IntegerField(source='villages.count', read_only=True)

    class Meta:
        model = Taluka
        fields = [
            'id', 'district', 'district_name', 'district_name_gu', 'state_name',
            'taluka_name', 'taluka_name_gu', 'taluka_code', 'latitude', 'longitude', 'village_count',
            'created_at', 'updated_at'
        ]


class DistrictSerializer(serializers.ModelSerializer):
    state_name = serializers.ReadOnlyField(source='state.state_name')
    taluka_count = serializers.IntegerField(source='talukas.count', read_only=True)

    class Meta:
        model = District
        fields = [
            'id', 'state', 'state_name', 'district_name', 'district_name_gu', 'district_code',
            'latitude', 'longitude', 'taluka_count',
            'created_at', 'updated_at'
        ]


class StateSerializer(serializers.ModelSerializer):
    district_count = serializers.IntegerField(source='districts.count', read_only=True)

    class Meta:
        model = State
        fields = [
            'id', 'state_name', 'state_name_gu', 'state_code', 'latitude', 'longitude',
            'district_count', 'created_at', 'updated_at'
        ]
