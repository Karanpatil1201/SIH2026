from app.agents.master_agent import MasterAgent
from app.agents.ocean_agent import OceanAgent
from app.agents.weather_agent import WeatherAgent
from app.agents.satellite_agent import SatelliteAgent
from app.agents.fisheries_agent import FisheriesAgent
from app.agents.coral_agent import CoralAgent
from app.agents.vessel_agent import VesselAgent

def test_specialized_domain_agents():
    # 1. Ocean Agent
    ocean = OceanAgent()
    o_res = ocean.process(18.9667, 72.8333)
    assert o_res["agent"] == "Ocean Agent"
    assert o_res["status"] in ["SAFE", "CAUTION", "DANGER"]
    assert "wave_height" in o_res["findings"]
    assert len(o_res["reasons"]) > 0

    # 2. Weather Agent
    weather = WeatherAgent()
    w_res = weather.process(18.9667, 72.8333)
    assert w_res["agent"] == "Weather Agent"
    assert w_res["status"] in ["SAFE", "CAUTION", "DANGER"]
    assert "wind_speed" in w_res["findings"]

    # 3. Satellite Agent
    sat = SatelliteAgent()
    s_res = sat.process(18.9667, 72.8333)
    assert s_res["agent"] == "Satellite Agent"
    assert "turbidity_indicator" in s_res["findings"]

    # 4. Fisheries Agent
    fish = FisheriesAgent()
    f_res = fish.process(18.9667, 72.8333, o_res["findings"])
    assert f_res["agent"] == "Fisheries Agent"
    assert "pfz_indicator_score" in f_res["findings"]
    assert len(f_res["findings"]["target_species"]) > 0

    # 5. Coral Agent
    coral = CoralAgent()
    c_res = coral.process(18.9667, 72.8333, o_res["findings"])
    assert c_res["agent"] == "Coral Health Agent"
    assert "degree_heating_weeks" in c_res["findings"]

    # 6. Vessel Agent
    vessel = VesselAgent()
    v_res = vessel.process(18.9667, 72.8333, {**o_res["findings"], **w_res["findings"]})
    assert v_res["agent"] == "Vessel Agent"
    assert "vessel_class_risks" in v_res["findings"]

def test_master_orchestrator_agent_execution():
    ma = MasterAgent()
    trace = ma.process_query("What is the marine risk near Mumbai tomorrow?", 18.9667, 72.8333)
    assert trace.query == "What is the marine risk near Mumbai tomorrow?"
    assert len(trace.execution_steps) >= 6
    assert trace.final_risk_assessment is not None
    assert 0.0 <= trace.final_risk_assessment.risk_score <= 100.0
    assert trace.final_risk_assessment.risk_level in ["SAFE", "CAUTION", "DANGER", "LOW", "MODERATE", "HIGH", "CRITICAL"]

def test_master_agent_status_registry():
    ma = MasterAgent()
    statuses = ma.get_all_agents_status()
    assert len(statuses) >= 6
    agent_ids = [s["agent_id"] for s in statuses]
    assert "ocean_agent" in agent_ids
    assert "weather_agent" in agent_ids
    assert "satellite_agent" in agent_ids
    assert "fisheries_agent" in agent_ids
    assert "coral_agent" in agent_ids
    assert "vessel_agent" in agent_ids
