from app.agents.master_agent import MasterAgent
from app.risk.risk_engine import RiskEngine

def test_location_safety_analysis():
    ma = MasterAgent()
    # Test valid marine coordinates (Mumbai offshore)
    res = ma.analyse_location(18.9667, 72.8333, mode="HYBRID")
    
    assert res["latitude"] == 18.9667
    assert res["longitude"] == 72.8333
    assert res["risk_level"] in ["SAFE", "CAUTION", "DANGER"]
    assert 0.0 <= res["risk_score"] <= 100.0
    assert 0 <= res["confidence"] <= 100
    assert "current_conditions" in res
    assert "wave_height_m" in res["current_conditions"]
    assert "wind_speed_kmh" in res["current_conditions"]
    assert len(res["key_risks"]) > 0
    assert len(res["agent_findings"]) >= 6
    assert len(res["recommendations"]) > 0
    assert "collaborative_reasoning" in res

def test_predictive_area_scan():
    ma = MasterAgent()
    scan_res = ma.scan_area(18.9667, 72.8333, radius_km=50.0, mode="HYBRID")
    
    assert scan_res["center"]["latitude"] == 18.9667
    assert scan_res["radius_km"] == 50.0
    assert len(scan_res["directional_scans"]) == 8
    
    directions = [s["direction"] for s in scan_res["directional_scans"]]
    assert "N" in directions and "S" in directions and "E" in directions and "W" in directions
    assert len(scan_res["predictive_threat_summary"]) > 0

def test_predictive_route_analysis():
    ma = MasterAgent()
    route_res = ma.analyse_route(
        origin_lat=18.9667, origin_lon=72.8333,
        dest_lat=15.4989, dest_lon=73.8278,
        origin_name="Mumbai Port", dest_name="Goa Port",
        mode="HYBRID"
    )
    
    assert route_res["total_distance_km"] > 0
    assert route_res["overall_route_safety"] in ["SAFE", "CAUTION", "DANGER"]
    assert len(route_res["progressive_checkpoints"]) >= 3
    
    labels = [cp["label"] for cp in route_res["progressive_checkpoints"]]
    assert "CURRENT LOCATION" in labels
    assert any("KM AHEAD" in l for l in labels) or any("DESTINATION" in l for l in labels)

def test_central_risk_engine_thresholds():
    engine = RiskEngine()
    
    # Safe condition test
    safe_data = {
        "sst": 28.0, "wave_height": 0.8, "wave_period": 7.0, "swell_height": 0.5,
        "current_velocity": 0.3, "wind_speed": 12.0, "pressure": 1014.0,
        "precipitation": 0.0, "salinity": 35.2, "chlorophyll": 0.45, "sea_level": 0.05
    }
    safe_res = engine.calculate_risk(safe_data)
    assert safe_res["risk_score"] <= 35.0
    assert safe_res["risk_level"] in ["SAFE", "CAUTION"]
    
    # Severe danger condition test
    danger_data = {
        "sst": 30.5, "wave_height": 4.5, "wave_period": 11.0, "swell_height": 3.2,
        "current_velocity": 2.1, "wind_speed": 65.0, "pressure": 978.0,
        "precipitation": 45.0, "salinity": 34.0, "chlorophyll": 1.2, "sea_level": 0.8
    }
    danger_res = engine.calculate_risk(danger_data)
    assert danger_res["risk_score"] >= 60.0
    assert danger_res["risk_level"] == "DANGER"
