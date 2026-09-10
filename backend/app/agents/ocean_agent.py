from typing import Dict, Any, List
from app.providers.openmeteo import OpenMeteoMarineProvider
from app.providers.copernicus import CopernicusMarineService
from app.providers.demo import DemoOceanProvider

class OceanAgent:
    """
    Ocean Agent responsible for inspecting Sea Surface Temperature (SST),
    waves, swell, ocean currents, salinity, sea level, and marine anomalies.
    """
    def __init__(self):
        self.name = "Ocean Agent"
        self.live_provider = OpenMeteoMarineProvider()
        self.copernicus_provider = CopernicusMarineService()

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
            data = self.live_provider.get_ocean_data(lat, lon, target_time=target_time, force_refresh=force_refresh)

            # Open-Meteo does not expose salinity or chlorophyll. Enrich its live
            # record with authenticated Copernicus observations when available.
            copernicus_live = self.copernicus_provider.get_live_ocean_data(lat, lon)
            if copernicus_live:
                openmeteo_source = (data or {}).get("source", "open-meteo")
                data = {**(data or {}), **{key: value for key, value in copernicus_live.items() if value is not None}}
                data["source"] = f"{openmeteo_source} + Copernicus Marine Live"
        
        if not data and mode in ["HYBRID", "DEMO"]:
            data = self.copernicus_provider.get_ocean_data(lat, lon)
        
        if not data:
            data = DemoOceanProvider.get_demo_record(lat, lon)

        wave_h = float(data.get("wave_height", 1.2) or 1.2)
        current_v = float(data.get("current_velocity", 0.4) or 0.4)
        sst = float(data.get("sst", 28.5) or 28.5)

        reasons: List[str] = []
        recommendations: List[str] = []

        if wave_h >= 2.8 or current_v >= 1.5:
            status = "DANGER"
            reasons.append(f"Elevated wave height ({wave_h}m) or rapid current velocity ({current_v} m/s) detected.")
            recommendations.append("Severe sea state; avoid small vessel transit in this sector.")
        elif wave_h >= 1.8 or current_v >= 0.8:
            status = "CAUTION"
            reasons.append(f"Moderate wave height ({wave_h}m) and current speed ({current_v} m/s).")
            recommendations.append("Exercise caution and monitor swell elevation.")
        else:
            status = "SAFE"
            reasons.append(f"Calm ocean conditions: Wave height {wave_h}m, Current velocity {current_v} m/s.")
            recommendations.append("Normal sea conditions favorable for marine activities.")

        findings = {
            "sst": sst,
            "wave_height": wave_h,
            "wave_period": data.get("wave_period", 7.0),
            "swell_height": data.get("swell_height", 0.8),
            "current_velocity": current_v,
            "current_direction": data.get("current_direction", 180.0),
            "salinity": data.get("salinity", 35.2),
            "chlorophyll": data.get("chlorophyll", 0.45),
            "sea_level": data.get("sea_level", 0.1),
            "source": data.get("source", "open-meteo"),
            "status": data.get("status", "LIVE"),
            "live_data_available": data.get("live_data_available", True),
            "fetched_at": data.get("fetched_at"),
            "is_forecast": data.get("is_forecast", False),
            "forecast_target": data.get("forecast_target"),
            "salinity_source": "Copernicus Marine Live" if data.get("salinity") is not None and "Copernicus" in data.get("source", "") else "fallback",
            "chlorophyll_source": "Copernicus Marine Live" if data.get("chlorophyll") is not None and "Copernicus" in data.get("source", "") else "fallback",
            "mode": data.get("mode", "LIVE")
        }

        evidence = {
            "wave_height_m": wave_h,
            "current_velocity_ms": current_v,
            "sst_celsius": sst,
            "source": data.get("source")
        }

        confidence = 0.94 if data.get("mode") == "LIVE" else 0.85

        return {
            "agent": self.name,
            "status": status,
            "confidence": confidence,
            "findings": findings,
            "evidence": evidence,
            "reasons": reasons,
            "recommendations": recommendations
        }
