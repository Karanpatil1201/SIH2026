from typing import Dict, Any, List
from app.providers.openmeteo import OpenMeteoWeatherProvider
from app.providers.demo import DemoOceanProvider

class WeatherAgent:
    """
    Weather Agent responsible for inspecting wind speed, direction,
    air pressure, precipitation, storms, and atmospheric conditions.
    """
    def __init__(self):
        self.name = "Weather Agent"
        self.live_provider = OpenMeteoWeatherProvider()

    def process(
        self,
        lat: float,
        lon: float,
        mode: str = "HYBRID",
        target_time: Optional[str] = None,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        data = None
        if mode in ["LIVE", "HYBRID"]:
            data = self.live_provider.get_weather_data(lat, lon, target_time=target_time, force_refresh=force_refresh)
        
        if not data:
            demo_rec = DemoOceanProvider.get_demo_record(lat, lon)
            data = {
                "source": "demo_fallback",
                "status": "DEMO_FALLBACK",
                "live_data_available": False,
                "fetched_at": demo_rec.get("fetched_at"),
                "wind_speed": demo_rec.get("wind_speed", 18.5),
                "wind_direction": demo_rec.get("wind_direction", 240.0),
                "pressure": demo_rec.get("pressure", 1012.0),
                "precipitation": demo_rec.get("precipitation", 0.0),
                "air_temperature": 29.2,
                "humidity": 80.0,
                "cloud_cover": 40.0,
                "mode": "DEMO_FALLBACK"
            }

        wind_s = float(data.get("wind_speed", 15.0) or 15.0)
        pressure = float(data.get("pressure", 1012.0) or 1012.0)
        precip = float(data.get("precipitation", 0.0) or 0.0)

        reasons: List[str] = []
        recommendations: List[str] = []

        if wind_s >= 35.0 or pressure <= 995.0 or precip >= 25.0:
            status = "DANGER"
            reasons.append(f"Gale force winds ({wind_s} km/h) or low barometric pressure ({pressure} hPa) indicating storm forcing.")
            recommendations.append("Severe weather advisory active; suspend open water navigation.")
        elif wind_s >= 22.0 or pressure <= 1005.0 or precip >= 5.0:
            status = "CAUTION"
            reasons.append(f"Moderate to fresh breeze ({wind_s} km/h) and lowering pressure ({pressure} hPa).")
            recommendations.append("Monitor updated weather bulletins for squall alerts.")
        else:
            status = "SAFE"
            reasons.append(f"Favorable atmospheric state: Wind speed {wind_s} km/h, Barometric pressure {pressure} hPa.")
            recommendations.append("Stable weather parameters; clear for maritime operations.")

        findings = {
            "wind_speed": wind_s,
            "wind_direction": data.get("wind_direction", 240.0),
            "pressure": pressure,
            "precipitation": precip,
            "air_temperature": data.get("air_temperature", 28.5),
            "humidity": data.get("humidity", 78.0),
            "cloud_cover": data.get("cloud_cover", 30.0),
            "source": data.get("source", "open-meteo"),
            "status": data.get("status", "LIVE"),
            "live_data_available": data.get("live_data_available", True),
            "fetched_at": data.get("fetched_at"),
            "is_forecast": data.get("is_forecast", False),
            "forecast_target": data.get("forecast_target"),
            "mode": data.get("mode", "LIVE")
        }

        evidence = {
            "wind_speed_kmh": wind_s,
            "surface_pressure_hpa": pressure,
            "precipitation_mm": precip,
            "source": data.get("source")
        }

        confidence = 0.93 if data.get("mode") == "LIVE" else 0.84

        return {
            "agent": self.name,
            "status": status,
            "confidence": confidence,
            "findings": findings,
            "evidence": evidence,
            "reasons": reasons,
            "recommendations": recommendations
        }
