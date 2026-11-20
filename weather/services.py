import time
import requests
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from django.conf import settings
from .models import WeatherRecord

WMO_WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def decode_wmo_code(code):
    return WMO_WEATHER_CODES.get(int(code) if code is not None else 0, "Unknown / Variable")


def format_sun_time(iso_str):
    """Convert ISO time string like '2026-11-17T06:48' to '6:48 AM'."""
    if not iso_str:
        return None
    try:
        if 'T' in str(iso_str):
            t_part = str(iso_str).split('T')[1]
            h, m = map(int, t_part.split(':')[:2])
            period = "AM" if h < 12 else "PM"
            h_12 = h % 12
            if h_12 == 0:
                h_12 = 12
            return f"{h_12}:{m:02d} {period}"
    except Exception:
        pass
    return str(iso_str)


class WeatherService:
    OPEN_METEO_BASE_URL = getattr(settings, 'OPEN_METEO_BASE_URL', 'https://api.open-meteo.com/v1/forecast')
    OPENWEATHER_BASE_URL = getattr(settings, 'OPENWEATHER_BASE_URL', 'https://api.openweathermap.org/data/2.5')
    OPENWEATHER_API_KEY = getattr(settings, 'OPENWEATHER_API_KEY', '')

    # Backend in-memory caching to minimize external API calls
    LIVE_CACHE_TTL = 900  # 15 minutes
    FORECAST_CACHE_TTL = 1800  # 30 minutes
    _live_cache = {}
    _forecast_cache = {}

    @classmethod
    def fetch_live_weather(cls, latitude, longitude, state="Gujarat", district="Unknown", taluka=None, village=None):
        """
        Fetch current weather from cache or external API (Open-Meteo / OpenWeather).
        Caches results for 15 minutes to reduce API latency and server load.
        """
        lat = round(float(latitude), 4)
        lon = round(float(longitude), 4)
        cache_key = (round(lat, 2), round(lon, 2))

        # 0. Check cache
        now_ts = time.time()
        if cache_key in cls._live_cache:
            entry = cls._live_cache[cache_key]
            if now_ts - entry["time"] < cls.LIVE_CACHE_TTL:
                cached_data = dict(entry["data"])
                cached_data["is_cached"] = True
                return {
                    "success": True,
                    "created": False,
                    "record_id": cached_data.get("id"),
                    "data": cached_data
                }

        # 1. Try OpenWeather API if key configured
        if cls.OPENWEATHER_API_KEY:
            try:
                ow_url = f"{cls.OPENWEATHER_BASE_URL}/weather"
                params = {
                    "lat": lat,
                    "lon": lon,
                    "appid": cls.OPENWEATHER_API_KEY,
                    "units": "metric"
                }
                res = requests.get(ow_url, params=params, timeout=6)
                if res.status_code == 200:
                    ow_data = res.json()
                    main = ow_data.get("main", {})
                    wind = ow_data.get("wind", {})
                    clouds = ow_data.get("clouds", {})
                    sys_data = ow_data.get("sys", {})
                    weather_list = ow_data.get("weather", [{}])
                    cond = weather_list[0].get("main", "Clear") if weather_list else "Clear"

                    recorded_at = datetime.now(timezone.utc)
                    sunrise_ts = sys_data.get("sunrise")
                    sunset_ts = sys_data.get("sunset")
                    sunrise_str = datetime.fromtimestamp(sunrise_ts, tz=timezone.utc).strftime("%I:%M %p") if sunrise_ts else None
                    sunset_str = datetime.fromtimestamp(sunset_ts, tz=timezone.utc).strftime("%I:%M %p") if sunset_ts else None

                    record, created = WeatherRecord.objects.get_or_create(
                        latitude=lat,
                        longitude=lon,
                        recorded_at=recorded_at,
                        defaults={
                            "state": state,
                            "district": district if district != "Unknown" else ow_data.get("name", "Unknown"),
                            "taluka": taluka or "",
                            "village": village or "",
                            "temperature": main.get("temp", 0.0),
                            "feels_like": main.get("feels_like"),
                            "humidity": main.get("humidity", 0.0),
                            "rainfall": ow_data.get("rain", {}).get("1h", 0.0),
                            "wind_speed": wind.get("speed", 0.0),
                            "wind_direction": wind.get("deg"),
                            "pressure": main.get("pressure"),
                            "weather_condition": cond,
                            "data_source": "OpenWeather Site API",
                            "is_manual": False
                        }
                    )

                    visibility_m = ow_data.get("visibility")
                    visibility_km = round(visibility_m / 1000.0, 1) if visibility_m is not None else None

                    payload = {
                        "id": record.id,
                        "state": record.state,
                        "district": record.district,
                        "taluka": record.taluka,
                        "village": record.village,
                        "latitude": record.latitude,
                        "longitude": record.longitude,
                        "temperature": record.temperature,
                        "feels_like": record.feels_like,
                        "temp_max": main.get("temp_max"),
                        "temp_min": main.get("temp_min"),
                        "humidity": record.humidity,
                        "rainfall": record.rainfall,
                        "rainfall_mm": record.rainfall,
                        "wind_speed": record.wind_speed,
                        "wind_direction": record.wind_direction,
                        "pressure": record.pressure,
                        "cloud_cover": clouds.get("all", 0),
                        "uv_index": 0.0,
                        "visibility_km": visibility_km,
                        "visibility": f"{visibility_km} km" if visibility_km else None,
                        "sunrise": sunrise_str,
                        "sunset": sunset_str,
                        "weather_condition": record.weather_condition,
                        "recorded_at": record.recorded_at.isoformat(),
                        "last_updated": record.recorded_at.astimezone(ZoneInfo("Asia/Kolkata")).strftime("%I:%M %p"),
                        "data_source": record.data_source,
                        "is_manual": record.is_manual,
                        "is_cached": False
                    }

                    cls._live_cache[cache_key] = {"time": now_ts, "data": payload}
                    return {"success": True, "created": created, "record_id": record.id, "data": payload}
            except Exception as e:
                pass

        # 2. Open-Meteo live API (Standard primary weather source)
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,weather_code,surface_pressure,wind_speed_10m,wind_direction_10m,cloud_cover,uv_index,visibility",
            "daily": "sunrise,sunset,temperature_2m_max,temperature_2m_min",
            "timezone": "Asia/Kolkata"
        }

        try:
            response = requests.get(cls.OPEN_METEO_BASE_URL, params=params, timeout=6)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            # Fallback to most recent database record for this location if external API fails
            latest = WeatherRecord.objects.filter(
                latitude__gte=lat - 0.25, latitude__lte=lat + 0.25,
                longitude__gte=lon - 0.25, longitude__lte=lon + 0.25
            ).order_by('-recorded_at').first()

            if not latest and district and district != "Unknown":
                latest = WeatherRecord.objects.filter(district__icontains=district).order_by('-recorded_at').first()

            if latest:
                fallback_data = {
                    "id": latest.id,
                    "state": latest.state,
                    "district": latest.district,
                    "taluka": latest.taluka,
                    "village": latest.village,
                    "latitude": latest.latitude,
                    "longitude": latest.longitude,
                    "temperature": latest.temperature,
                    "feels_like": latest.feels_like,
                    "temp_max": latest.temperature + 2.0,
                    "temp_min": latest.temperature - 5.0,
                    "humidity": latest.humidity,
                    "rainfall": latest.rainfall,
                    "rainfall_mm": latest.rainfall,
                    "wind_speed": latest.wind_speed,
                    "wind_direction": latest.wind_direction,
                    "pressure": latest.pressure,
                    "cloud_cover": 10,
                    "uv_index": 5.0,
                    "visibility_km": 10.0,
                    "visibility": "10 km",
                    "sunrise": "6:30 AM",
                    "sunset": "6:15 PM",
                    "weather_condition": latest.weather_condition,
                    "recorded_at": latest.recorded_at.isoformat(),
                    "last_updated": latest.recorded_at.astimezone(ZoneInfo("Asia/Kolkata")).strftime("%I:%M %p"),
                    "data_source": "Database Recent Record (Offline Fallback)",
                    "is_manual": latest.is_manual,
                    "is_cached": True
                }
                return {"success": True, "created": False, "record_id": latest.id, "data": fallback_data}

            return {"success": False, "error": f"Live weather API temporarily unreachable: {str(e)}"}

        current = data.get("current", {})
        daily = data.get("daily", {})
        time_str = current.get("time")
        if time_str:
            recorded_at = datetime.fromisoformat(time_str)
            if recorded_at.tzinfo is None:
                recorded_at = recorded_at.replace(tzinfo=ZoneInfo("Asia/Kolkata"))
        else:
            recorded_at = datetime.now(timezone.utc)

        weather_condition = decode_wmo_code(current.get("weather_code", 0))

        # Check for existing record to avoid duplicate
        record, created = WeatherRecord.objects.get_or_create(
            latitude=lat,
            longitude=lon,
            recorded_at=recorded_at,
            defaults={
                "state": state,
                "district": district if district != "Unknown" else "Gujarat",
                "taluka": taluka or "",
                "village": village or "",
                "temperature": current.get("temperature_2m", 0.0),
                "feels_like": current.get("apparent_temperature"),
                "humidity": current.get("relative_humidity_2m", 0.0),
                "rainfall": current.get("rain") or current.get("precipitation") or 0.0,
                "wind_speed": current.get("wind_speed_10m", 0.0),
                "wind_direction": current.get("wind_direction_10m"),
                "pressure": current.get("surface_pressure"),
                "weather_condition": weather_condition,
                "data_source": "Open-Meteo Live API",
                "is_manual": False
            }
        )

        sunrises = daily.get("sunrise", [])
        sunsets = daily.get("sunset", [])
        max_temps = daily.get("temperature_2m_max", [])
        min_temps = daily.get("temperature_2m_min", [])

        sunrise_str = format_sun_time(sunrises[0]) if sunrises else "6:30 AM"
        sunset_str = format_sun_time(sunsets[0]) if sunsets else "6:15 PM"
        temp_max_val = max_temps[0] if max_temps else None
        temp_min_val = min_temps[0] if min_temps else None

        visibility_m = current.get("visibility")
        visibility_km = round(visibility_m / 1000.0, 1) if visibility_m is not None else None

        payload = {
            "id": record.id,
            "state": record.state,
            "district": record.district,
            "taluka": record.taluka,
            "village": record.village,
            "latitude": record.latitude,
            "longitude": record.longitude,
            "temperature": record.temperature,
            "feels_like": record.feels_like,
            "temp_max": temp_max_val,
            "temp_min": temp_min_val,
            "humidity": record.humidity,
            "rainfall": record.rainfall,
            "rainfall_mm": record.rainfall,
            "wind_speed": record.wind_speed,
            "wind_direction": record.wind_direction,
            "pressure": record.pressure,
            "cloud_cover": current.get("cloud_cover", 0),
            "uv_index": current.get("uv_index", 0.0),
            "visibility_km": visibility_km,
            "visibility": f"{visibility_km} km" if visibility_km else None,
            "sunrise": sunrise_str,
            "sunset": sunset_str,
            "weather_condition": record.weather_condition,
            "recorded_at": record.recorded_at.isoformat(),
            "last_updated": record.recorded_at.astimezone(ZoneInfo("Asia/Kolkata")).strftime("%I:%M %p"),
            "data_source": record.data_source,
            "is_manual": record.is_manual,
            "is_cached": False
        }

        # Cache valid response
        cls._live_cache[cache_key] = {"time": now_ts, "data": payload}

        return {
            "success": True,
            "created": created,
            "record_id": record.id,
            "data": payload
        }

    @classmethod
    def fetch_forecast(cls, latitude, longitude, days=7):
        """
        Fetch multi-day weather forecast from OpenWeather or Open-Meteo API.
        """
        lat = round(float(latitude), 4)
        lon = round(float(longitude), 4)

        if cls.OPENWEATHER_API_KEY:
            try:
                ow_url = f"{cls.OPENWEATHER_BASE_URL}/forecast"
                params = {"lat": lat, "lon": lon, "appid": cls.OPENWEATHER_API_KEY, "units": "metric"}
                res = requests.get(ow_url, params=params, timeout=8)
                if res.status_code == 200:
                    data = res.json()
                    item_list = data.get("list", [])
                    daily_map = {}
                    for item in item_list:
                        dt_txt = item.get("dt_txt", "")
                        date_str = dt_txt.split(" ")[0] if " " in dt_txt else dt_txt
                        if not date_str:
                            continue
                        if date_str not in daily_map:
                            daily_map[date_str] = {
                                "temps": [],
                                "rain": 0.0,
                                "winds": [],
                                "weather": item.get("weather", [{}])[0].get("main", "Clear")
                            }
                        daily_map[date_str]["temps"].append(item.get("main", {}).get("temp", 0))
                        daily_map[date_str]["winds"].append(item.get("wind", {}).get("speed", 0))
                        if "rain" in item and "3h" in item["rain"]:
                            daily_map[date_str]["rain"] += item["rain"]["3h"]

                    forecast_list = []
                    for date_k, v in list(daily_map.items())[:int(days)]:
                        forecast_list.append({
                            "date": date_k,
                            "weather_condition": v["weather"],
                            "weather_code": 0,
                            "temperature_max": round(max(v["temps"]), 1) if v["temps"] else None,
                            "temperature_min": round(min(v["temps"]), 1) if v["temps"] else None,
                            "precipitation_sum_mm": round(v["rain"], 1),
                            "precipitation_probability_pct": 20 if v["rain"] > 0 else 0,
                            "wind_speed_max_kmh": round(max(v["winds"]) * 3.6, 1) if v["winds"] else 0.0,
                        })

                    if forecast_list:
                        return {
                            "success": True,
                            "latitude": lat,
                            "longitude": lon,
                            "forecast_days": len(forecast_list),
                            "forecast": forecast_list
                        }
            except Exception as e:
                print(f"OpenWeather forecast failed: {e}")

        # Open-Meteo forecast fallback
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max",
            "forecast_days": min(max(int(days), 1), 16),
            "timezone": "Asia/Kolkata"
        }

        try:
            response = requests.get(cls.OPEN_METEO_BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            return {"success": False, "error": f"Weather API request failed: {str(e)}"}

        daily = data.get("daily", {})
        dates = daily.get("time", [])
        weather_codes = daily.get("weather_code", [])
        max_temps = daily.get("temperature_2m_max", [])
        min_temps = daily.get("temperature_2m_min", [])
        rain_sums = daily.get("precipitation_sum", [])
        rain_probs = daily.get("precipitation_probability_max", [])
        wind_speeds = daily.get("wind_speed_10m_max", [])

        forecast_list = []
        for i in range(len(dates)):
            w_code = weather_codes[i] if i < len(weather_codes) else 0
            forecast_list.append({
                "date": dates[i],
                "weather_condition": decode_wmo_code(w_code),
                "weather_code": w_code,
                "temperature_max": max_temps[i] if i < len(max_temps) else None,
                "temperature_min": min_temps[i] if i < len(min_temps) else None,
                "precipitation_sum_mm": rain_sums[i] if i < len(rain_sums) else 0.0,
                "precipitation_probability_pct": rain_probs[i] if i < len(rain_probs) else 0,
                "wind_speed_max_kmh": wind_speeds[i] if i < len(wind_speeds) else 0.0,
            })

        return {
            "success": True,
            "latitude": params["latitude"],
            "longitude": params["longitude"],
            "forecast_days": len(forecast_list),
            "forecast": forecast_list
        }

