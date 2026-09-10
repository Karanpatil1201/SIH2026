from app.gis.spatial_engine import SpatialEngine
from app.agents.geofencing_agent import GeofencingAgent

def test_imbl_proximity_detection():
    engine = SpatialEngine()
    # Coordinates very close to India-Pakistan IMBL (Sir Creek offshore sector: 23.35, 67.90)
    inspection = engine.inspect_point_geofences(23.35, 67.90)
    assert len(inspection["imbl_warnings"]) > 0
    assert inspection["imbl_warnings"][0]["id"] == "IMBL_IN_PK"

def test_restricted_zone_detection():
    agent = GeofencingAgent()
    # Coordinates inside Mumbai Naval & BARC Exclusion Zone (18.95, 72.85)
    result = agent.process(18.95, 72.85)
    assert result["status"] == "DANGER"
    assert len(result["findings"]["restricted_violations"]) > 0
    assert "Mumbai Harbour" in result["findings"]["restricted_violations"][0]["name"]

def test_clear_marine_waters():
    agent = GeofencingAgent()
    # Safe open-sea coordinate off Ratnagiri (16.99, 73.10)
    result = agent.process(16.99, 73.10)
    assert result["status"] == "SAFE"
    assert result["findings"]["is_geofence_compliant"] is True

def test_route_geofence_intersection():
    agent = GeofencingAgent()
    # Route traversing Mumbai Naval restricted zone
    bad_route = [
        {"lat": 18.85, "lon": 72.75},
        {"lat": 18.95, "lon": 72.85},  # inside restricted
        {"lat": 19.05, "lon": 72.95}
    ]
    check = agent.verify_route(bad_route)
    assert check["is_blocked"] is True
    assert check["is_compliant"] is False
    assert "restricted" in check["rejection_reason"].lower()
