"""
VARUNA Geofencing & Boundary Compliance Agent
Responsible for spatial compliance against:
- International Maritime Boundary Lines (IMBL)
- Restricted Military / Industrial Waters
- Marine Protected Areas (MPAs)
- Ecologically Sensitive Zones (ESZs)
"""

from typing import Dict, Any, List
from app.gis.spatial_engine import SpatialEngine
from app.gis.spatial_data import (
    IMBL_BOUNDARIES,
    RESTRICTED_ZONES,
    MARINE_PROTECTED_AREAS,
    ECOLOGICALLY_SENSITIVE_ZONES
)

class GeofencingAgent:
    """
    Geofencing Agent verifying maritime vessel positioning and navigation compliance.
    """

    def __init__(self):
        self.name = "Geofencing Agent"
        self.spatial_engine = SpatialEngine()

    def process(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Evaluates geofencing constraints for a single coordinate point.
        """
        inspection = self.spatial_engine.inspect_point_geofences(lat, lon)
        reasons: List[str] = []
        recommendations: List[str] = []
        status = "SAFE"

        # Check Restricted Waters
        if inspection["restricted_violations"]:
            status = "DANGER"
            for v in inspection["restricted_violations"]:
                reasons.append(f"VIOLATION: Position falls within restricted zone '{v['name']}' ({v['category']}).")
                recommendations.append(f"Evacuate {v['name']} immediately: {v['reason']}")

        # Check IMBL Proximity
        for w in inspection["imbl_warnings"]:
            if w["severity"] == "CRITICAL":
                status = "DANGER"
                reasons.append(f"CRITICAL IMBL PROXIMITY: {w['distance_km']} km from {w['name']}.")
                recommendations.append(w["advisory"])
            elif w["severity"] == "WARNING" and status != "DANGER":
                status = "CAUTION"
                reasons.append(f"IMBL ALERT: Vessel is {w['distance_km']} km from {w['name']}.")
                recommendations.append(w["advisory"])

        # Check MPA Overlaps
        if inspection["mpa_overlaps"]:
            if status == "SAFE":
                status = "CAUTION"
            for mpa in inspection["mpa_overlaps"]:
                reasons.append(f"MPA OVERLAP: Located within {mpa['name']} ({mpa['category']}).")
                recommendations.append(f"Commercial trawling prohibited within MPA buffer: {mpa['reason']}")

        # Check ESZ Overlaps
        if inspection["esz_overlaps"]:
            if status == "SAFE":
                status = "CAUTION"
            for esz in inspection["esz_overlaps"]:
                reasons.append(f"ECOLOGICAL ZONE: Located within {esz['name']}.")
                recommendations.append(f"Observe speed reduction and coral protection protocols: {esz['reason']}")

        if not reasons:
            reasons.append("Geofence check passed: Point is in clear waters outside restricted, IMBL, and MPA zones.")
            recommendations.append("Maintain standard navigational awareness and AIS transmission.")

        findings = {
            "is_geofence_compliant": inspection["is_geofence_compliant"],
            "imbl_warnings": inspection["imbl_warnings"],
            "restricted_violations": inspection["restricted_violations"],
            "mpa_overlaps": inspection["mpa_overlaps"],
            "esz_overlaps": inspection["esz_overlaps"],
            "nearest_port": inspection["nearest_port"],
            "status": status
        }

        return {
            "agent": self.name,
            "status": status,
            "confidence": 0.98,
            "findings": findings,
            "reasons": reasons,
            "recommendations": recommendations
        }

    def verify_route(self, waypoints: List[Dict[str, float]]) -> Dict[str, Any]:
        """
        Inspects an entire route (list of {'lat': float, 'lon': float}) for geofence breaches.
        Returns whether route is compliant or must be REJECTED.
        """
        violations = []
        warnings = []
        is_blocked = False

        if len(waypoints) < 2:
            return {"is_compliant": True, "violations": [], "warnings": []}

        for i in range(len(waypoints) - 1):
            p1_lat = waypoints[i]["lat"]
            p1_lon = waypoints[i]["lon"]
            p2_lat = waypoints[i + 1]["lat"]
            p2_lon = waypoints[i + 1]["lon"]

            # 1. Check Restricted Zones
            for r_zone in RESTRICTED_ZONES:
                if self.spatial_engine.route_segment_intersects_polygon(p1_lat, p1_lon, p2_lat, p2_lon, r_zone["polygon"]):
                    violations.append({
                        "zone_id": r_zone["id"],
                        "name": r_zone["name"],
                        "category": r_zone["category"],
                        "segment_index": i,
                        "reason": f"Route segment {i+1} intersects restricted military/industrial zone: {r_zone['name']}"
                    })
                    if r_zone.get("hard_block", True):
                        is_blocked = True

            # 2. Check MPA Overlaps
            for mpa in MARINE_PROTECTED_AREAS:
                if self.spatial_engine.route_segment_intersects_polygon(p1_lat, p1_lon, p2_lat, p2_lon, mpa["polygon"]):
                    warnings.append({
                        "zone_id": mpa["id"],
                        "name": mpa["name"],
                        "category": mpa["category"],
                        "segment_index": i,
                        "reason": f"Route traverses Marine Protected Area: {mpa['name']} ({mpa['reason']})"
                    })

        return {
            "is_compliant": not is_blocked,
            "is_blocked": is_blocked,
            "violations": violations,
            "warnings": warnings,
            "rejection_reason": violations[0]["reason"] if violations else None
        }
