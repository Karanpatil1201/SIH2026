from typing import Dict, Any, List
from app.providers.satellite import SatelliteDataService

class SatelliteAgent:
    """
    Satellite Agent responsible for satellite observation interpretation,
    ocean colour anomaly indicators, turbidity, and potential algal bloom indicators.
    """
    def __init__(self):
        self.name = "Satellite Agent"
        self.service = SatelliteDataService()

    def process(self, lat: float, lon: float, ocean_data: Dict[str, Any] = None, mode: str = "LIVE") -> Dict[str, Any]:
        if mode in ["LIVE", "HYBRID"] and ocean_data and ocean_data.get("chlorophyll_source") == "Copernicus Marine Live":
            data = {
                "source": "Copernicus Marine BGC Live",
                "chlorophyll": ocean_data.get("chlorophyll"),
                "turbidity": "Live chlorophyll observation; turbidity unavailable",
                "bloom_indicator": "Live chlorophyll signal",
                "anomaly_confidence": 0.88,
                "mode": "LIVE",
            }
        else:
            data = self.service.get_satellite_data(lat, lon, mode=mode)
        turbidity = data.get("turbidity", "Low oceanic turbidity")
        bloom = data.get("bloom_indicator", "Low bloom risk")
        chlorophyll = data.get("chlorophyll", 0.5)

        reasons: List[str] = []
        recommendations: List[str] = []

        if "bloom" in bloom.lower() and "possible" in bloom.lower():
            status = "CAUTION"
            reasons.append(f"Satellite radiometric anomaly: {bloom} detected via Sentinel-3 / MODIS.")
            recommendations.append("Conduct ground-truthed water sampling in high-reflectance anomaly cells.")
        elif "moderate" in turbidity.lower() or "high" in turbidity.lower():
            status = "CAUTION"
            reasons.append(f"Elevated optical turbidity ({turbidity}) in coastal shelf.")
            recommendations.append("Exercise caution near shallow bathymetry plumes.")
        else:
            status = "SAFE"
            reasons.append("Standard ocean colour profile and clean optical reflectance indices.")
            recommendations.append("Normal optical water clarity; no satellite anomaly flags.")

        findings = {
            "turbidity_indicator": turbidity,
            "bloom_indicator": bloom,
            "chlorophyll_sat": chlorophyll,
            "confidence": data.get("anomaly_confidence", 0.88),
            "source": data.get("source", "Sentinel-3 OLCI / MODIS Aqua")
        }

        evidence = {
            "satellite_source": data.get("source"),
            "chlorophyll_sat_mg_m3": chlorophyll,
            "optical_turbidity": turbidity
        }

        return {
            "agent": self.name,
            "status": status,
            "confidence": float(data.get("anomaly_confidence", 0.88)),
            "findings": findings,
            "evidence": evidence,
            "reasons": reasons,
            "recommendations": recommendations
        }
