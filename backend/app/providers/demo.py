from typing import Dict, Any, List
from datetime import datetime, timezone

class DemoOceanProvider:
    """
    Curated high-fidelity synthetic demo data generator for offline/fallback mode.
    Pre-configured for Mumbai, Goa, Bay of Bengal, and Indian Ocean regions.
    """

    KNOWN_LOCATIONS = {
        "Mumbai": {"lat": 18.9667, "lon": 72.8333, "sst": 28.8, "wave_height": 2.4, "wind_speed": 34.0, "risk_score": 68.0},
        "Goa": {"lat": 15.4989, "lon": 73.8278, "sst": 29.2, "wave_height": 1.5, "wind_speed": 18.5, "risk_score": 38.0},
        "Kochi": {"lat": 9.9312, "lon": 76.2673, "sst": 29.5, "wave_height": 1.2, "wind_speed": 14.2, "risk_score": 25.0},
        "Visakhapatnam": {"lat": 17.6868, "lon": 83.2185, "sst": 29.0, "wave_height": 2.8, "wind_speed": 42.0, "risk_score": 79.0},
        "Port Blair": {"lat": 11.6233, "lon": 92.7264, "sst": 29.4, "wave_height": 3.1, "wind_speed": 48.0, "risk_score": 85.0},
    }

    @classmethod
    def get_demo_record(cls, lat: float, lon: float) -> Dict[str, Any]:
        # Match closest known location or synthesize spatial variation
        closest_loc = "Arabian Sea Offshore"
        min_dist = 999.0
        base_vals = {"sst": 28.5, "wave_height": 1.8, "wind_speed": 22.0}

        for name, loc in cls.KNOWN_LOCATIONS.items():
            d = ((lat - loc["lat"])**2 + (lon - loc["lon"])**2)**0.5
            if d < min_dist:
                min_dist = d
                closest_loc = name
                base_vals = loc

        now_iso = datetime.now(timezone.utc).isoformat()
        return {
            "source": "demo_fallback",
            "provider": "VARUNA High-Resolution Synthetic Ocean Model (Offline Fallback)",
            "status": "DEMO_FALLBACK",
            "live_data_available": False,
            "fetched_at": now_iso,
            "timestamp": now_iso,
            "latitude": lat,
            "longitude": lon,
            "location_name": closest_loc,
            "sst": base_vals["sst"],
            "wave_height": base_vals["wave_height"],
            "wave_direction": 245.0,
            "wave_period": 7.5,
            "swell_height": round(base_vals["wave_height"] * 0.6, 2),
            "current_velocity": 0.58,
            "current_direction": 195.0,
            "wind_speed": base_vals["wind_speed"],
            "wind_direction": 255.0,
            "pressure": 1009.5 if base_vals["wind_speed"] > 35 else 1013.0,
            "precipitation": 4.5 if base_vals["wind_speed"] > 35 else 0.0,
            "salinity": 35.4,
            "chlorophyll": 0.65 if lat > 17 else 0.38,
            "sea_level": 0.18,
            "mode": "DEMO_FALLBACK"
        }
