from typing import Dict, Any
from app.gis.pathfinding import RoutePathfinder

class RouteAgent:
    """
    Route Agent calculating risk-aware marine routes between ports or coordinates.
    Evaluates wave risk, wind risk, current, storm risk, advisory severity, and distance
    to produce Fastest, Safest, and Balanced routes.
    """
    def __init__(self):
        self.pathfinder = RoutePathfinder()

    def process(
        self,
        origin_lat: float = 18.9667,
        origin_lon: float = 72.8333,
        dest_lat: float = 15.4989,
        dest_lon: float = 73.8278,
        origin_name: str = "Mumbai Port",
        dest_name: str = "Goa Port"
    ) -> Dict[str, Any]:
        result = self.pathfinder.find_routes(origin_lat, origin_lon, dest_lat, dest_lon, origin_name, dest_name)
        return {
            "agent": "RouteAgent",
            "status": "COMPLETED",
            "findings": {
                "route_comparison": result.model_dump(),
                "recommended_route_id": result.recommended_route_id,
                "recommendation_reason": result.recommendation_reason
            }
        }
