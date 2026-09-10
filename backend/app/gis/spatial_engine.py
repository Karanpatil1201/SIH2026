"""
VARUNA Marine Spatial GIS Engine
Provides mathematical algorithms for:
- Haversine great-circle distance (km)
- Ray-casting Point-in-Polygon (PIP) testing
- Point-to-segment perpendicular distance (km)
- Polyline boundary proximity (IMBL)
- Line segment intersection with spatial polygons (Route Geofencing)
- Comprehensive spatial proximity lookups
"""

import math
from typing import List, Dict, Tuple, Any, Optional
from app.gis.spatial_data import (
    IMBL_BOUNDARIES,
    RESTRICTED_ZONES,
    MARINE_PROTECTED_AREAS,
    ECOLOGICALLY_SENSITIVE_ZONES,
    COASTAL_PORTS_AND_HARBOURS
)

class SpatialEngine:
    """
    High-performance pure-Python geospatial analysis engine.
    Compatible with PostGIS standards (ST_Distance, ST_Intersects, ST_Contains).
    """

    @staticmethod
    def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate great-circle distance between two GPS coordinates in kilometers."""
        R = 6371.0  # Earth's radius in km
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_phi / 2.0) ** 2 +
            math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2)
        )
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return round(R * c, 2)

    @staticmethod
    def point_in_polygon(lat: float, lon: float, polygon: List[List[float]]) -> bool:
        """
        Ray-casting algorithm to determine whether point (lat, lon) is inside polygon [[lat, lon], ...].
        """
        n = len(polygon)
        inside = False
        p1_lat, p1_lon = polygon[0]

        for i in range(1, n + 1):
            p2_lat, p2_lon = polygon[i % n]
            if min(p1_lon, p2_lon) < lon <= max(p1_lon, p2_lon):
                # Calculate latitude of intersection with horizontal ray
                if p1_lon != p2_lon:
                    x_inters = (lon - p1_lon) * (p2_lat - p1_lat) / (p2_lon - p1_lon) + p1_lat
                else:
                    x_inters = p1_lat

                if p1_lat == p2_lat or lat <= x_inters:
                    inside = not inside
            p1_lat, p1_lon = p2_lat, p2_lon

        return inside

    @staticmethod
    def point_to_segment_distance_km(
        p_lat: float, p_lon: float,
        a_lat: float, a_lon: float,
        b_lat: float, b_lon: float
    ) -> float:
        """Perpendicular distance from point P to line segment AB in kilometers."""
        # Convert to local Cartesian approximation (accurate for < 500km)
        # 1 deg lat ~ 111 km, 1 deg lon ~ 111 * cos(lat) km
        mid_lat = math.radians((a_lat + b_lat) / 2.0)
        kx = 111.320 * math.cos(mid_lat)
        ky = 110.574

        px, py = p_lon * kx, p_lat * ky
        ax, ay = a_lon * kx, a_lat * ky
        bx, by = b_lon * kx, b_lat * ky

        dx = bx - ax
        dy = by - ay

        if dx == 0.0 and dy == 0.0:
            return math.hypot(px - ax, py - ay)

        # Parameter t of projection onto line
        t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
        proj_x = ax + t * dx
        proj_y = ay + t * dy

        return round(math.hypot(px - proj_x, py - proj_y), 2)

    @classmethod
    def distance_to_polyline_km(cls, lat: float, lon: float, polyline: List[List[float]]) -> float:
        """Calculates the minimum distance from point to a multi-segment polyline."""
        if len(polyline) < 2:
            return 9999.0

        min_dist = float('inf')
        for i in range(len(polyline) - 1):
            a_lat, a_lon = polyline[i]
            b_lat, b_lon = polyline[i + 1]
            d = cls.point_to_segment_distance_km(lat, lon, a_lat, a_lon, b_lat, b_lon)
            if d < min_dist:
                min_dist = d

        return round(min_dist, 2)

    @classmethod
    def line_segments_intersect(
        cls,
        p1_lat: float, p1_lon: float, p2_lat: float, p2_lon: float,
        q1_lat: float, q1_lon: float, q2_lat: float, q2_lon: float
    ) -> bool:
        """2D Orientation test to check if segment P1-P2 intersects segment Q1-Q2."""
        def ccw(a, b, c):
            return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])

        p1 = (p1_lat, p1_lon)
        p2 = (p2_lat, p2_lon)
        q1 = (q1_lat, q1_lon)
        q2 = (q2_lat, q2_lon)

        return ccw(p1, q1, q2) != ccw(p2, q1, q2) and ccw(p1, p2, q1) != ccw(p1, p2, q2)

    @classmethod
    def route_segment_intersects_polygon(
        cls,
        lat1: float, lon1: float,
        lat2: float, lon2: float,
        polygon: List[List[float]]
    ) -> bool:
        """Checks if a route segment (lat1, lon1) -> (lat2, lon2) intersects or lies inside a polygon."""
        # Check if either endpoint is inside
        if cls.point_in_polygon(lat1, lon1, polygon) or cls.point_in_polygon(lat2, lon2, polygon):
            return True

        # Check segment intersection with polygon edges
        n = len(polygon)
        for i in range(n):
            e1_lat, e1_lon = polygon[i]
            e2_lat, e2_lon = polygon[(i + 1) % n]
            if cls.line_segments_intersect(lat1, lon1, lat2, lon2, e1_lat, e1_lon, e2_lat, e2_lon):
                return True

        # Midpoint check
        mid_lat = (lat1 + lat2) / 2.0
        mid_lon = (lon1 + lon2) / 2.0
        if cls.point_in_polygon(mid_lat, mid_lon, polygon):
            return True

        return False

    @classmethod
    def inspect_point_geofences(cls, lat: float, lon: float) -> Dict[str, Any]:
        """
        Evaluates a single coordinate point against all GIS layers:
        - IMBL proximity (<10km warning, <3km critical)
        - Restricted waters containment
        - Marine Protected Area (MPA) containment
        - Ecologically Sensitive Zone (ESZ) containment
        - Nearest port/harbour lookup
        """
        imbl_warnings = []
        restricted_violations = []
        mpa_overlaps = []
        esz_overlaps = []

        # 1. IMBL Proximity Check
        for imbl in IMBL_BOUNDARIES:
            dist = cls.distance_to_polyline_km(lat, lon, imbl["coordinates"])
            if dist <= imbl["critical_threshold_km"]:
                imbl_warnings.append({
                    "id": imbl["id"],
                    "name": imbl["name"],
                    "distance_km": dist,
                    "severity": "CRITICAL",
                    "advisory": f"CRITICAL: Within {dist} km of {imbl['name']}. Immediate course correction advised.",
                    "region": imbl["region"]
                })
            elif dist <= imbl["warning_threshold_km"]:
                imbl_warnings.append({
                    "id": imbl["id"],
                    "name": imbl["name"],
                    "distance_km": dist,
                    "severity": "WARNING",
                    "advisory": f"WARNING: Approaching {imbl['name']} ({dist} km away). Maintain vigilance.",
                    "region": imbl["region"]
                })

        # 2. Restricted Waters Check
        for r_zone in RESTRICTED_ZONES:
            if cls.point_in_polygon(lat, lon, r_zone["polygon"]):
                restricted_violations.append({
                    "id": r_zone["id"],
                    "name": r_zone["name"],
                    "category": r_zone["category"],
                    "reason": r_zone["reason"],
                    "hard_block": r_zone["hard_block"]
                })

        # 3. MPA Check
        for mpa in MARINE_PROTECTED_AREAS:
            if cls.point_in_polygon(lat, lon, mpa["polygon"]):
                mpa_overlaps.append({
                    "id": mpa["id"],
                    "name": mpa["name"],
                    "state": mpa["state"],
                    "category": mpa["category"],
                    "reason": mpa["reason"],
                    "restricted_fishing": mpa.get("restricted_commercial_fishing", True)
                })

        # 4. ESZ Check
        for esz in ECOLOGICALLY_SENSITIVE_ZONES:
            if cls.point_in_polygon(lat, lon, esz["polygon"]):
                esz_overlaps.append({
                    "id": esz["id"],
                    "name": esz["name"],
                    "state": esz["state"],
                    "category": esz["category"],
                    "reason": esz["reason"]
                })

        # 5. Nearest Port
        nearest_port = None
        min_p_dist = float('inf')
        for port in COASTAL_PORTS_AND_HARBOURS:
            d = cls.haversine_km(lat, lon, port["lat"], port["lon"])
            if d < min_p_dist:
                min_p_dist = d
                nearest_port = {**port, "distance_km": d}

        is_safe_geofence = (
            len(restricted_violations) == 0 and
            len([w for w in imbl_warnings if w["severity"] == "CRITICAL"]) == 0
        )

        return {
            "latitude": lat,
            "longitude": lon,
            "is_geofence_compliant": is_safe_geofence,
            "imbl_warnings": imbl_warnings,
            "restricted_violations": restricted_violations,
            "mpa_overlaps": mpa_overlaps,
            "esz_overlaps": esz_overlaps,
            "nearest_port": nearest_port
        }
