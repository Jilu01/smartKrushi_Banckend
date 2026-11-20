"""
SmartKrushi – Backend API Integration Test
Run: backend/venv/Scripts/python.exe backend/test_apis.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.test import Client
c = Client()

PASS = "✅"
FAIL = "❌"

def test(name, response, expected_status=200, checks=None):
    ok = response.status_code == expected_status
    sym = PASS if ok else FAIL
    print(f"{sym} [{response.status_code}] {name}")
    if ok and checks and response.status_code == 200:
        try:
            d = response.json()
            for key, label in checks.items():
                val = d
                for part in key.split('.'):
                    val = val.get(part, None) if isinstance(val, dict) else None
                print(f"      {label}: {val}")
        except Exception as e:
            print(f"      (parse error: {e})")
    elif not ok:
        try:
            print(f"      Body: {response.content[:200]}")
        except Exception:
            pass

print("\n" + "="*55)
print("  SmartKrushi Backend API Integration Tests")
print("="*55 + "\n")

# 1. Location Detect (Vadodara)
r = c.get('/api/v1/location/detect/', {'latitude': '22.3', 'longitude': '73.2'})
test("Location Detect (22.3, 73.2 – Vadodara area)",
     r, checks={"district": "District", "taluka": "Taluka", "village": "Village"})

# 2. Location Detect (Surat)
r = c.get('/api/v1/location/detect/', {'latitude': '21.17', 'longitude': '72.83'})
test("Location Detect (21.17, 72.83 – Surat area)", r,
     checks={"district": "District", "taluka": "Taluka"})

# 3. Location Hierarchy
r = c.get('/api/v1/location/hierarchy/')
test("Location Hierarchy", r)
if r.status_code == 200:
    d = r.json()
    print(f"      districts={len(d.get('districts', []))}, talukas={len(d.get('talukas', []))}, villages={len(d.get('villages', []))}")

# 4. Districts List
r = c.get('/api/v1/locations/districts/')
test("Districts List", r)
if r.status_code == 200:
    d = r.json()
    total = len(d) if isinstance(d, list) else d.get('count', len(d.get('results', [])))
    print(f"      total={total}")

# 5. Weather Current (Ahmedabad)
r = c.get('/api/v1/weather/current/', {'latitude': '23.0225', 'longitude': '72.5714', 'district': 'Ahmedabad'})
test("Weather Current (Ahmedabad)", r,
     checks={"temperature": "Temp (C)", "humidity": "Humidity %", "sunrise": "Sunrise", "sunset": "Sunset", "last_updated": "Last Updated"})

# 6. Weather Details (Surat)
r = c.get('/api/v1/weather/details/', {'latitude': '21.17', 'longitude': '72.83', 'district': 'Surat'})
test("Weather Details (Surat)", r)
if r.status_code == 200:
    d = r.json()
    cur = d.get('current') or {}
    print(f"      temp={cur.get('temperature')}, forecast_days={len(d.get('forecast', []))}")

# 7. Soil by district (Ahmedabad)
r = c.get('/api/v1/soil/location/', {'district': 'Ahmedabad'})
test("Soil – Ahmedabad", r,
     checks={"resolution_level": "Resolution", "soil_type": "Soil Type", "soil_ph": "pH"})

# 8. Soil by district (Rajkot)
r = c.get('/api/v1/soil/location/', {'district': 'Rajkot'})
test("Soil – Rajkot", r,
     checks={"resolution_level": "Resolution", "soil_type": "Soil Type"})

# 9. Soil by coordinates
r = c.get('/api/v1/soil/location/', {'latitude': '23.0225', 'longitude': '72.5714'})
test("Soil – By Coordinates", r,
     checks={"resolution_level": "Resolution", "soil_type": "Soil Type"})

# 10. Crop Recommendations (Ahmedabad)
r = c.get('/api/v1/crops/recommendations/', {'district': 'Ahmedabad'})
test("Crop Recommendations (Ahmedabad)", r)
if r.status_code == 200:
    d = r.json()
    recs = d.get('recommendations', [])
    print(f"      count={len(recs)}")
    for rec in recs[:3]:
        print(f"      → {rec.get('crop_name')} ({rec.get('suitability_score')}%): {rec.get('recommendation_reason', '')[:60]}")

# 11. Crop Recommendations (Kutch – arid)
r = c.get('/api/v1/crops/recommendations/', {'district': 'Kutch'})
test("Crop Recommendations (Kutch)", r)
if r.status_code == 200:
    d = r.json()
    recs = d.get('recommendations', [])
    print(f"      count={len(recs)}, top={recs[0].get('crop_name') if recs else 'none'}")

# 12. Fertilizer Recommendations (Ahmedabad)
r = c.get('/api/v1/fertilizers/recommendations/', {'district': 'Ahmedabad'})
test("Fertilizer Recommendations (Ahmedabad)", r,
     checks={"success": "Success", "deficiency_summary": "Deficiencies"})

# 13. Crops List
r = c.get('/api/v1/crops/')
test("Crops List", r)
if r.status_code == 200:
    d = r.json()
    items = d if isinstance(d, list) else d.get('results', [])
    print(f"      total={len(items)}")

# 14. 404 for bad location
r = c.get('/api/v1/soil/location/', {'district': 'NonExistentPlace123'})
print(f"{'✅' if r.status_code in [200, 404] else '❌'} [{r.status_code}] Soil – Bad location (graceful)")

print("\n" + "="*55)
print("  Tests Complete")
print("="*55 + "\n")
