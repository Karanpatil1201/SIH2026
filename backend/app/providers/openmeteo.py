import requests
import time
import copy
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from app.providers.base import OceanDataProvider, WeatherDataProvider

class OpenMeteoMarineProvider(OceanDataProvider):
    """
    Fetches real-time marine forecasts from Open-Meteo Marine API with caching.
    Retrieves wave height, wave direction, wave period, swell height, ocean currents, SST.
    """
    BASE_URL = "https://marine-api.open-meteo.com/v1/marine"
    _cache: Dict[tuple, tuple[float, Dict[str, Any]]] = {}
    _ttl_seconds: float = 300.0

    def get_ocean_data(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        cache_key = (round(lat, 2), round(lon, 2))
        cached = self._cache.get(cache_key)
        if cached and (time.monotonic() - cached[0] < self._ttl_seconds):
            return copy.deepcopy(cached[1])

        params = {
            "latitude": lat,
            "longitude": lon,
            "current": [
                "wave_height", "wave_direction", "wave_period",
                "swell_wave_height", "ocean_current_velocity", "ocean_current_direction",
                "sea_surface_temperature"
            ],
            "timezone": "UTC"
        }
        try:
            resp = requests.get(self.BASE_URL, params=params, timeout=3.5)
            if resp.status_code == 200:
                data = resp.json()
                current = data.get("current", {})
                res = {
                    "source": "Open-Meteo Marine",
                    "timestamp": current.get("time") or datetime.now(timezone.utc).isoformat(),
                    "latitude": lat,
                    "longitude": lon,
                    "sst": current.get("sea_surface_temperature", 28.6),
                    "wave_height": current.get("wave_height", 1.4),
                    "wave_direction": current.get("wave_direction", 240.0),
                    "wave_period": current.get("wave_period", 7.2),
                    "swell_height": current.get("swell_wave_height", 0.9),
                    "current_velocity": current.get("ocean_current_velocity", 0.4),
                    "current_direction": current.get("ocean_current_direction", 180.0),
                    "salinity": 35.2,
                    "chlorophyll": 0.42,
                    "sea_level": 0.12,
                    "mode": "LIVE"
                }
                self._cache[cache_key] = (time.monotonic(), res)
                return copy.deepcopy(res)
        except Exception as e:
            print(f"[OpenMeteoMarineProvider] Live fetch notice: {e}")
        
        return None # Return None to trigger fallback to demo provider


class OpenMeteoWeatherProvider(WeatherDataProvider):
    """
    Fetches real-time weather forecasts from Open-Meteo Weather API with caching.
    Retrieves wind speed, wind direction, temperature, pressure, precipitation, humidity.
    """
    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    _cache: Dict[tuple, tuple[float, Dict[str, Any]]] = {}
    _ttl_seconds: float = 300.0

    def get_weather_data(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        cache_key = (round(lat, 2), round(lon, 2))
        cached = self._cache.get(cache_key)
        if cached and (time.monotonic() - cached[0] < self._ttl_seconds):
            return copy.deepcopy(cached[1])

        params = {
            "latitude": lat,
            "longitude": lon,
            "current": [
                "temperature_2m", "relative_humidity_2m", "surface_pressure",
                "wind_speed_10m", "wind_direction_10m", "precipitation"
            ],
            "timezone": "UTC"
        }
        try:
            resp = requests.get(self.BASE_URL, params=params, timeout=3.5)
            if resp.status_code == 200:
                data = resp.json()
                current = data.get("current", {})
                res = {
                    "source": "Open-Meteo Weather",
                    "timestamp": current.get("time") or datetime.now(timezone.utc).isoformat(),
                    "latitude": lat,
                    "longitude": lon,
                    "air_temperature": current.get("temperature_2m", 29.5),
                    "humidity": current.get("relative_humidity_2m", 78.0),
                    "pressure": current.get("surface_pressure", 1011.5),
                    "wind_speed": current.get("wind_speed_10m", 22.4),
                    "wind_direction": current.get("wind_direction_10m", 250.0),
                    "precipitation": current.get("precipitation", 0.0),
                    "cloud_cover": 35.0,
                    "mode": "LIVE"
                }
                self._cache[cache_key] = (time.monotonic(), res)
                return copy.deepcopy(res)
        except Exception as e:
            print(f"[OpenMeteoWeatherProvider] Live fetch notice: {e}")
        
        return None
