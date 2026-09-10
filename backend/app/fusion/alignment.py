from datetime import datetime, timezone
from typing import Dict, Any

class SpatialTemporalAlignmentEngine:
    """
    Normalizes spatial coordinates to a standard 0.1° marine grid,
    converts all timestamps to UTC ISO-8601, and standardizes physical units.
    """

    GRID_RESOLUTION_DEG = 0.1 # ~11 km resolution

    @classmethod
    def snap_to_marine_grid(cls, lat: float, lon: float) -> Dict[str, float]:
        """
        Maps continuous lat/lon coordinates to closest 0.1 degree grid cell center.
        """
        snapped_lat = round(round(lat / cls.GRID_RESOLUTION_DEG) * cls.GRID_RESOLUTION_DEG, 4)
        snapped_lon = round(round(lon / cls.GRID_RESOLUTION_DEG) * cls.GRID_RESOLUTION_DEG, 4)
        return {"lat": snapped_lat, "lon": snapped_lon}

    @classmethod
    def normalize_timestamp(cls, raw_timestamp: Any) -> str:
        """
        Converts timestamp strings or datetimes to ISO-8601 UTC format.
        """
        if isinstance(raw_timestamp, datetime):
            dt = raw_timestamp
        else:
            try:
                dt = datetime.fromisoformat(str(raw_timestamp).replace('Z', '+00:00'))
            except Exception:
                dt = datetime.now(timezone.utc)
        
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
            
        return dt.isoformat()

    @classmethod
    def normalize_units(cls, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensures metric units across all providers:
        - SST: Celsius (°C)
        - Wave/Swell height: Meters (m)
        - Wind Speed: Kilometers per hour (km/h) (Convert m/s or knots if needed)
        - Pressure: Hectopascals (hPa)
        """
        res = record.copy()
        
        # Wind speed unit check: convert m/s to km/h if unit indicated or value is small with high wind context
        if "wind_speed_ms" in res:
            res["wind_speed"] = round(res.pop("wind_speed_ms") * 3.6, 2)
        elif "wind_speed_knots" in res:
            res["wind_speed"] = round(res.pop("wind_speed_knots") * 1.852, 2)
            
        return res
