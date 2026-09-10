from app.gis.pathfinding import RoutePathfinder

def test_route_pathfinding_and_selection():
    pathfinder = RoutePathfinder()
    routes_res = pathfinder.find_routes(
        origin_lat=18.9667, origin_lon=72.8333,
        dest_lat=15.4989, dest_lon=73.8278,
        origin_name="Mumbai Port", dest_name="Goa Port"
    )

    assert len(routes_res.routes) >= 2
    assert routes_res.recommended_route_id in ["R_SAFE", "R_BAL", "R_FAST"]
    assert routes_res.origin["name"] == "Mumbai Port"

def test_departure_time_optimization():
    pathfinder = RoutePathfinder()
    dep_opt = pathfinder.optimize_departure_windows(lat=16.9902, lon=73.2980)

    assert "departure_windows" in dep_opt
    assert len(dep_opt["departure_windows"]) >= 5
    assert dep_opt["recommended_window"] in ["08:30", "10:00", "08:00"]
    assert "NOT recommended" in dep_opt["recommendation"]
