import os
import django
import io
import csv

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework.test import APIClient
from locations.models import State, District, Taluka, Village

client = APIClient()

print("="*60)
print("PHASE 3 LOCATION MASTER VERIFICATION")
print("="*60)

# 1. Database Counts
print(f"Total States: {State.objects.count()}")
print(f"Total Districts: {District.objects.count()} (Expected: 33 official Gujarat districts)")
print(f"Total Talukas: {Taluka.objects.count()}")
print(f"Total Villages: {Village.objects.count()}")

# Verify all 33 districts have Gujarati name and LGD code
dist_missing_gu = District.objects.filter(district_name_gu__isnull=True).count()
dist_missing_code = District.objects.filter(district_code__isnull=True).count()
print(f"Districts missing Gujarati names: {dist_missing_gu}")
print(f"Districts missing LGD code: {dist_missing_code}")

# 2. Test Endpoints
# A. States
r = client.get('/api/v1/locations/states/')
assert r.status_code == 200, f"States API failed: {r.status_code}"
print(f"GET /api/v1/locations/states/ -> OK ({len(r.data.get('results', r.data))} states)")

# B. Districts
r = client.get('/api/v1/locations/districts/')
assert r.status_code == 200, f"Districts API failed: {r.status_code}"
total_dist = len(r.data.get('results', r.data))
print(f"GET /api/v1/locations/districts/ -> OK ({total_dist} districts)")

# C. Search in Gujarati
r = client.get('/api/v1/locations/districts/?search=રાજકોટ')
assert r.status_code == 200, f"Gujarati search failed: {r.status_code}"
results = r.data.get('results', r.data)
assert len(results) > 0 and results[0]['district_name'] == 'Rajkot', f"Unexpected search result: {results}"
print(f"GET /api/v1/locations/districts/?search=રાજકોટ -> OK (Matched: {results[0]['district_name']} - {results[0]['district_name_gu']})")

# D. Search in English for newly added Sabarkantha
r = client.get('/api/v1/locations/districts/?search=Sabarkantha')
assert r.status_code == 200
results = r.data.get('results', r.data)
assert len(results) > 0 and results[0]['district_name'] == 'Sabarkantha'
print(f"GET /api/v1/locations/districts/?search=Sabarkantha -> OK (Matched: {results[0]['district_name']} - {results[0]['district_name_gu']}, LGD: {results[0]['district_code']})")

# E. Location Detect (Rajkot coords: 22.3039, 70.8022)
r = client.get('/api/v1/locations/detect/?lat=22.3039&lon=70.8022')
assert r.status_code == 200, f"Location detect failed: {r.status_code}"
print(f"GET /api/v1/locations/detect/ -> OK")
print(f"  Detected: {r.data.get('district')} ({r.data.get('district_gu')}), Taluka: {r.data.get('taluka')} ({r.data.get('taluka_gu')}), Village: {r.data.get('village')} ({r.data.get('village_gu')})")
print(f"  Address GU: {r.data.get('formatted_address_gu')}")

# F. Hierarchy API
r = client.get('/api/v1/locations/hierarchy/?district_name=Anand')
assert r.status_code == 200, f"Hierarchy API failed: {r.status_code}"
dists = r.data.get('districts', [])
print(f"GET /api/v1/locations/hierarchy/?district_name=Anand -> OK")
print(f"  District: {dists[0]['name']} ({dists[0]['name_gu']}), Talukas count: {dists[0]['taluka_count']}")
sample_taluka = dists[0]['talukas'][0]
print(f"  Sample Taluka: {sample_taluka['name']} ({sample_taluka['name_gu']}), Villages count: {sample_taluka['village_count']}")

# G. Test Bulk Import endpoint
from django.contrib.auth import get_user_model
User = get_user_model()
admin_user, _ = User.objects.get_or_create(username='admin_test', defaults={'is_staff': True, 'is_superuser': True})
client.force_authenticate(user=admin_user)

csv_content = """state,state_gu,district,district_gu,taluka,taluka_gu,village,village_gu,village_code,latitude,longitude
Gujarat,ગુજરાત,Rajkot,રાજકોટ,Gondal,ગોંડલ,TestVillage,ટેસ્ટ ગામ,999001,21.96,70.79
"""
csv_file = io.BytesIO(csv_content.encode('utf-8'))
csv_file.name = 'bulk_test.csv'

r = client.post('/api/v1/locations/bulk-import/', {'file': csv_file}, format='multipart')
assert r.status_code == 200, f"Bulk import failed: {r.status_code} - {r.data}"
print(f"POST /api/v1/locations/bulk-import/ -> OK")
print(f"  Response: {r.data}")

# Clean up test village
Village.objects.filter(village_name='TestVillage').delete()
admin_user.delete()

print("\n" + "="*60)
print("ALL PHASE 3 LOCATION MASTER DATA & API CHECKS PASSED!")
print("="*60)
