"""
VARUNA Marine Grid Graph
Enhanced spatial marine navigation grid covering Arabian Sea, Bay of Bengal, and Indian Ocean coastal corridors.
"""

import math
from typing import List, Dict, Tuple, Any
from app.gis.spatial_engine import SpatialEngine

class MarineGridCell:
    def __init__(self, lat: float, lon: float, wave_h: float = 1.2, wind_s: float = 18.0, risk: float = 25.0):
        self.lat = round(lat, 2)
        self.lon = round(lon, 2)
        self.wave_height = wave_h
        self.wind_speed = wind_s
        self.risk_score = risk
        self.is_restricted = False
        self.is_mpa = False

    def distance_to(self, other: 'MarineGridCell') -> float:
        return SpatialEngine.haversine_km(self.lat, self.lon, other.lat, other.lon)

class MarineGridGraph:
    """
    Graph representation of Indian Ocean marine navigation grid with geofence awareness.
    Grid cell step: ~0.3 degrees (~33 km nodes) for high-resolution pathfinding.
    """

    def __init__(self, min_lat: float = 7.0, max_lat: float = 24.0, min_lon: float = 67.0, max_lon: float = 93.0, step: float = 0.3):
        self.nodes: Dict[Tuple[float, float], MarineGridCell] = {}
        self.step = step
        self.spatial_engine = SpatialEngine()

        lat = min_lat
        while lat <= max_lat:
            lon = min_lon
            while lon <= max_lon:
                r_lat, r_lon = round(lat, 2), round(lon, 2)
                
                # Baseline physical conditions
                w_h = round(1.2 + 0.3 * math.sin(r_lat * 0.4), 2)
                w_s = round(15.0 + 5.0 * math.cos(r_lon * 0.3), 1)
                r_score = round((w_h / 3.0) * 40.0 + (w_s / 35.0) * 40.0, 1)

                cell = MarineGridCell(r_lat, r_lon, w_h, w_s, r_score)
                
                # Check GIS restricted and MPA status
                geo_insp = self.spatial_engine.inspect_point_geofences(r_lat, r_lon)
                if geo_insp["restricted_violations"]:
                    cell.is_restricted = True
                    cell.risk_score = 95.0
                if geo_insp["mpa_overlaps"]:
                    cell.is_mpa = True
                    cell.risk_score += 15.0

                self.nodes[(r_lat, r_lon)] = cell
                lon += step
            lat += step

    def get_cell(self, lat: float, lon: float) -> MarineGridCell:
        closest_key = min(self.nodes.keys(), key=lambda k: (k[0] - lat)**2 + (k[1] - lon)**2)
        return self.nodes[closest_key]

    def get_neighbors(self, cell: MarineGridCell) -> List[MarineGridCell]:
        neighbors = []
        for dlat in [-self.step, 0.0, self.step]:
            for dlon in [-self.step, 0.0, self.step]:
                if dlat == 0.0 and dlon == 0.0:
                    continue
                n_key = (round(cell.lat + dlat, 2), round(cell.lon + dlon, 2))
                if n_key in self.nodes:
                    neighbors.append(self.nodes[n_key])
        return neighbors
