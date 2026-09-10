from typing import Dict, Any, List
from datetime import datetime, timezone
from app.models.schemas import DataQualityReport

class DataQualityEngine:
    """
    Validates and monitors incoming marine & weather data.
    Enforces physical limits, coordinate validity, and timestamp freshness.
    Rejects impossible values (e.g. SST = -100°C).
    """

    # Physical boundaries for marine/meteorological parameters
    VALID_BOUNDS = {
        "sst": (-5.0, 45.0), # °C
        "wave_height": (0.0, 35.0), # meters
        "wave_direction": (0.0, 360.0), # degrees
        "wave_period": (0.0, 30.0), # seconds
        "swell_height": (0.0, 25.0), # meters
        "current_velocity": (0.0, 15.0), # m/s
        "wind_speed": (0.0, 250.0), # km/h
        "wind_direction": (0.0, 360.0), # degrees
        "pressure": (850.0, 1080.0), # hPa
        "salinity": (0.0, 45.0), # PSU
        "chlorophyll": (0.0, 100.0), # mg/m³
        "sea_level": (-10.0, 10.0), # meters
    }

    @classmethod
    def evaluate_quality(cls, data: Dict[str, Any]) -> DataQualityReport:
        missing_fields: List[str] = []
        anomalies: List[str] = []
        issues: List[str] = []
        deductions = 0.0

        # 1. Coordinate Validation
        lat = data.get("latitude")
        lon = data.get("longitude")
        if lat is None or lon is None or not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            issues.append(f"Invalid geographical coordinates: lat={lat}, lon={lon}")
            deductions += 40.0

        # 2. Field Completeness & Physical Boundary Checks
        for param, bounds in cls.VALID_BOUNDS.items():
            val = data.get(param)
            if val is None:
                missing_fields.append(param)
                deductions += 4.0
            else:
                min_b, max_b = bounds
                if val < min_b or val > max_b:
                    anomalies.append(param)
                    issues.append(f"Out of physical bounds for {param}: {val} (allowed: [{min_b}, {max_b}])")
                    deductions += 25.0

        # 3. Timestamp Freshness Check
        ts_str = data.get("timestamp")
        freshness_label = "LIVE"
        if ts_str:
            try:
                if isinstance(ts_str, datetime):
                    dt = ts_str
                else:
                    dt = datetime.fromisoformat(str(ts_str).replace('Z', '+00:00'))
                
                # Check age
                age_hours = (datetime.now(timezone.utc) - dt.replace(tzinfo=timezone.utc)).total_seconds() / 3600.0
                if age_hours < 3:
                    freshness_label = "LIVE"
                elif age_hours < 24:
                    freshness_label = "RECENT"
                elif age_hours < 72:
                    freshness_label = "DELAYED"
                    deductions += 10.0
                else:
                    freshness_label = "STALE"
                    issues.append(f"Data is stale ({round(age_hours, 1)} hours old)")
                    deductions += 20.0
            except Exception as e:
                issues.append(f"Unparseable timestamp: {ts_str}")
                deductions += 15.0

        quality_score = max(0.0, round(100.0 - deductions, 1))

        if quality_score >= 80.0:
            status = "VALID"
        elif quality_score >= 50.0:
            status = "WARNING"
        else:
            status = "INVALID"

        return DataQualityReport(
            quality_score=quality_score,
            status=status,
            missing_fields=missing_fields,
            anomalies=anomalies,
            freshness=freshness_label,
            issues=issues
        )
