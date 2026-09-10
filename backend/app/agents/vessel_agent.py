from typing import Dict, Any, List

class VesselAgent:
    """
    Vessel Agent responsible for assessing maritime vessel navigation safety,
    wave-wind tolerance limits across craft types, route hazards, and speed adjustments.
    """

    def __init__(self):
        self.name = "Vessel Agent"

    def process(self, lat: float, lon: float, marine_data: Dict[str, Any] = None) -> Dict[str, Any]:
        data = marine_data or {}
        wave_height = float(data.get("wave_height") or 1.2)
        swell_height = float(data.get("swell_height") or 0.8)
        wind_speed = float(data.get("wind_speed") or 15.0)
        current_velocity = float(data.get("current_velocity") or 0.5)
        wave_period = float(data.get("wave_period") or 7.0)

        reasons: List[str] = []
        recommendations: List[str] = []

        # Evaluate thresholds by craft class
        # Class 1: Artisanal / Small fishing vessels (<12m)
        # Class 2: Coastal shipping, tugs, trawlers (12-50m)
        # Class 3: Deep-sea commercial container / tankers (>50m)

        artisanal_risk = "DANGER" if wave_height >= 2.0 or wind_speed >= 25.0 else ("CAUTION" if wave_height >= 1.5 or wind_speed >= 18.0 else "SAFE")
        coastal_risk = "DANGER" if wave_height >= 3.5 or wind_speed >= 35.0 else ("CAUTION" if wave_height >= 2.5 or wind_speed >= 25.0 else "SAFE")
        deepsea_risk = "DANGER" if wave_height >= 5.0 or wind_speed >= 50.0 else ("CAUTION" if wave_height >= 3.5 or wind_speed >= 35.0 else "SAFE")

        # Overall Vessel Agent Status (driven by the most vulnerable class in active waters)
        if wave_height >= 3.0 or wind_speed >= 30.0:
            status = "DANGER"
            reasons.append(f"High sea state: Significant wave height {wave_height}m and wind speed {wind_speed} km/h.")
            recommendations.append("Small crafts strictly restricted. Medium vessels must reduce cruising speed by 30% and monitor swell.")
            speed_reduction_pct = 30.0
        elif wave_height >= 1.8 or wind_speed >= 20.0:
            status = "CAUTION"
            reasons.append(f"Moderate sea chop (Wave: {wave_height}m, Wind: {wind_speed} km/h).")
            recommendations.append("Small vessels exercise caution. Coastal shipping maintain standard watchkeeping.")
            speed_reduction_pct = 12.0
        else:
            status = "SAFE"
            reasons.append(f"Calm to slight sea state (Wave: {wave_height}m, Current: {current_velocity} m/s).")
            recommendations.append("All vessel classes clear for normal passage plan execution.")
            speed_reduction_pct = 0.0

        findings = {
            "vessel_class_risks": {
                "artisanal_craft_under_12m": artisanal_risk,
                "coastal_trawler_12_to_50m": coastal_risk,
                "commercial_deepsea_over_50m": deepsea_risk
            },
            "speed_reduction_recommended_pct": speed_reduction_pct,
            "wave_steepness_ratio": round(wave_height / max(4.0, wave_period * 1.5), 2),
            "navigational_clearance": "RESTRICTED" if status == "DANGER" else ("ADVISORY" if status == "CAUTION" else "CLEAR")
        }

        evidence = {
            "wave_height_m": wave_height,
            "swell_height_m": swell_height,
            "wind_speed_kmh": wind_speed,
            "current_velocity_ms": current_velocity
        }

        return {
            "agent": self.name,
            "status": status,
            "confidence": 0.91,
            "findings": findings,
            "evidence": evidence,
            "reasons": reasons,
            "recommendations": recommendations
        }
