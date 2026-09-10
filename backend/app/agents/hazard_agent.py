"""
VARUNA Unified Hazard & Proactive Alert Agent
Aggregates high waves, swell shears, wind gales, lightning strikes, and cyclone cones into proactive alerts.
Fulfills SIH Requirement #18.
"""

from typing import Dict, Any, List
from datetime import datetime, timezone

class HazardAgent:
    """
    Synthesizes physical marine hazards and produces structured actionable alert dossiers.
    """

    def __init__(self):
        self.name = "Hazard Agent"

    def process(
        self,
        lat: float,
        lon: float,
        ocean_data: Dict[str, Any] = None,
        weather_data: Dict[str, Any] = None,
        lightning_data: Dict[str, Any] = None,
        cyclone_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        ocean = ocean_data or {}
        weather = weather_data or {}
        lightning = lightning_data or {}
        cyclone = cyclone_data or {}

        wave_h = float(ocean.get("wave_height", 1.2) or 1.2)
        swell_h = float(ocean.get("swell_height", 0.8) or 0.8)
        wind_s = float(weather.get("wind_speed", 15.0) or 15.0)
        pressure = float(weather.get("pressure", 1012.0) or 1012.0)

        active_alerts: List[Dict[str, Any]] = []
        overall_severity = "SAFE"

        # 1. High Wave & Swell Check
        if wave_h >= 3.0:
            active_alerts.append({
                "hazard_type": "HIGH_WAVE_CRITICAL",
                "severity": "CRITICAL",
                "title": f"High Wave Hazard ({wave_h}m)",
                "description": f"Significant wave height ({wave_h}m) and swell ({swell_h}m) exceed safe operating limits for small/medium craft.",
                "action": "Suspend coastal and offshore fishing voyages. Commercial vessels reduce speed.",
                "source": "Open-Meteo Marine Physics + INCOIS Bulletin"
            })
            overall_severity = "DANGER"
        elif wave_h >= 2.0:
            active_alerts.append({
                "hazard_type": "HIGH_WAVE_ADVISORY",
                "severity": "WARNING",
                "title": f"Elevated Wave Advisory ({wave_h}m)",
                "description": f"Moderate wave chop ({wave_h}m) requiring heightened navigational caution.",
                "action": "Artisanal fishing craft remain vigilant; secure loose deck gear.",
                "source": "Open-Meteo Marine Physics"
            })
            if overall_severity != "DANGER":
                overall_severity = "CAUTION"

        # 2. Gale Wind Check
        if wind_s >= 35.0:
            active_alerts.append({
                "hazard_type": "GALE_FORCE_WIND",
                "severity": "CRITICAL",
                "title": f"Gale-Force Wind Alert ({wind_s} km/h)",
                "description": f"Sustained offshore wind gusts reaching {wind_s} km/h with heavy spray.",
                "action": "Small craft stay in port; large vessels adjust course heading.",
                "source": "Open-Meteo Weather Model"
            })
            overall_severity = "DANGER"
        elif wind_s >= 24.0:
            active_alerts.append({
                "hazard_type": "STRONG_WIND_WATCH",
                "severity": "WARNING",
                "title": f"Strong Wind Watch ({wind_s} km/h)",
                "description": f"Elevated wind velocity of {wind_s} km/h.",
                "action": "Check vessel stability and monitor weather radar.",
                "source": "Open-Meteo Weather Model"
            })
            if overall_severity != "DANGER":
                overall_severity = "CAUTION"

        # 3. Lightning Check
        l_status = lightning.get("status", "SAFE")
        if l_status == "DANGER":
            active_alerts.append({
                "hazard_type": "LIGHTNING_STRIKE_CRITICAL",
                "severity": "CRITICAL",
                "title": "Severe Lightning Activity Detected",
                "description": lightning.get("findings", {}).get("reasons", ["Convective electrical strikes nearby."])[0] if isinstance(lightning.get("findings", {}).get("reasons"), list) else "Convective lightning active.",
                "action": "Avoid open-deck exposure; lower high radio antennas.",
                "source": "IMD Convective Lightning Radar"
            })
            overall_severity = "DANGER"

        # 4. Cyclone Check
        c_status = cyclone.get("status", "SAFE")
        if c_status == "DANGER":
            active_alerts.append({
                "hazard_type": "CYCLONIC_STORM_DIRECT",
                "severity": "CRITICAL",
                "title": f"Active Cyclone Envelope ({cyclone.get('findings', {}).get('name', 'Storm')})",
                "description": f"User coordinates lie within dangerous proximity of active cyclonic center.",
                "action": "Enforce total maritime curfew and initiate emergency port shelter.",
                "source": "IMD / Joint Typhoon Warning Center"
            })
            overall_severity = "DANGER"

        return {
            "agent": self.name,
            "status": overall_severity,
            "confidence": 0.95,
            "active_alert_count": len(active_alerts),
            "alerts": active_alerts,
            "summary": f"Hazard synthesis complete: {len(active_alerts)} active alerts ({overall_severity} overall level)."
        }
