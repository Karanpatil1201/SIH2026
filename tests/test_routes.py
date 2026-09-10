from app.gis.pathfinding import RoutePathfinder

def test_route_pathfinding():
    pf = RoutePathfinder()
    res = pf.find_routes(18.9667, 72.8333, 15.4989, 73.8278, "Mumbai", "Goa")
    assert len(res.routes) == 3
    assert res.recommended_route_id in ["R_SAFE", "R_BAL", "R_FAST"]
    assert res.routes[0].total_distance_km > 100.0
