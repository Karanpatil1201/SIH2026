from typing import Dict, Any
from app.fusion.alignment import SpatialTemporalAlignmentEngine

class GISAgent:
    """
    GIS Agent responsible for coordinate resolution, spatial boundary queries,
    marine zone lookup, and snapping observations to standardized 0.1° marine grid cells.
    """
    def process(self, lat: float, lon: float) -> Dict[str, Any]:
        grid = SpatialTemporalAlignmentEngine.snap_to_marine_grid(lat, lon)
        
        # Resolve marine region name
        region = "Arabian Sea Offshore"
        if 18.0 <= lat <= 20.0 and 72.0 <= lon <= 73.5:
            region = "Mumbai Coastal Waters"
        elif 15.0 <= lat <= 16.5 and 73.0 <= lon <= 74.0:
            region = "Goa Coastal Waters"
        elif 16.0 <= lat <= 18.5 and 82.0 <= lon <= 85.0:
            region = "Bay of Bengal Offshore (Visakhapatnam Zone)"

        return {
            "agent": "GISAgent",
            "status": "COMPLETED",
            "findings": {
                "input_lat": lat,
                "input_lon": lon,
                "snapped_lat": grid["lat"],
                "snapped_lon": grid["lon"],
                "marine_region": region,
                "grid_cell_id": f"GRID_{grid['lat']}_{grid['lon']}"
            }
        }
