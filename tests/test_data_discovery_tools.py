from app.agents.data_discovery_agent import DataDiscoveryAgent
from app.agents.intent_context_agent import StructuredContext
from app.tools.registry import tool_registry
import app.tools.marine_tools  # Ensure tools are registered

def test_data_discovery_for_fishing_query():
    agent = DataDiscoveryAgent()
    ctx = StructuredContext(
        intent="fishing_safety_and_route",
        location_name="Ratnagiri",
        needs_pfz=True,
        needs_ocean=True,
        needs_weather=True,
        needs_route=True
    )
    plan = agent.discover_data_requirements(ctx)
    assert plan["required_dataset_count"] >= 4
    assert "get_ocean_forecast" in plan["selected_tools"]
    assert "get_pfz_candidates" in plan["selected_tools"]
    assert "calculate_safe_route" in plan["selected_tools"]

def test_tool_registry_invocation():
    tools = tool_registry.list_tools()
    assert len(tools) >= 10
    
    tool_names = [t["name"] for t in tools]
    assert "get_ocean_forecast" in tool_names
    assert "get_weather_forecast" in tool_names
    assert "check_geofence_and_boundaries" in tool_names
