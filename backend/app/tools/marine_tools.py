"""
VARUNA Concrete Marine Tools
Implements dynamic tools for autonomous invocation by the Master Agent.
"""

from typing import Dict, Any, List, Optional
from app.tools.registry import tool_registry

@tool_registry.register(
    name="get_ocean_forecast",
    description="Retrieve live ocean physical parameters (Wave height, period, direction, swell, currents, SST, salinity)",
    category="OCEAN"
)
def tool_get_ocean_forecast(lat: float, lon: float, mode: str = "HYBRID") -> Dict[str, Any]:
    from app.agents.ocean_agent import OceanAgent
    agent = OceanAgent()
    return agent.process(lat, lon, mode=mode)

@tool_registry.register(
    name="get_weather_forecast",
    description="Retrieve atmospheric meteorology (Wind speed, gusts, surface pressure, precipitation)",
    category="WEATHER"
)
def tool_get_weather_forecast(lat: float, lon: float, mode: str = "HYBRID") -> Dict[str, Any]:
    from app.agents.weather_agent import WeatherAgent
    agent = WeatherAgent()
    return agent.process(lat, lon, mode=mode)

@tool_registry.register(
    name="get_satellite_indicators",
    description="Retrieve Sentinel-3 / MODIS remote sensing indicators (Chlorophyll-a, turbidity index, thermal fronts)",
    category="SATELLITE"
)
def tool_get_satellite_indicators(lat: float, lon: float, mode: str = "HYBRID") -> Dict[str, Any]:
    from app.agents.satellite_agent import SatelliteAgent
    agent = SatelliteAgent()
    return agent.process(lat, lon, mode=mode)

@tool_registry.register(
    name="get_pfz_candidates",
    description="Discover and evaluate Potential Fishing Zone (PFZ) candidates with safety scores and species recommendations",
    category="FISHERIES"
)
def tool_get_pfz_candidates(lat: float, lon: float, ocean_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    from app.agents.fisheries_agent import FisheriesAgent
    agent = FisheriesAgent()
    return agent.process(lat, lon, ocean_data)

@tool_registry.register(
    name="check_geofence_and_boundaries",
    description="Inspect vessel/location compliance against IMBL, restricted naval zones, MPAs, and ESZs",
    category="GIS"
)
def tool_check_geofence_and_boundaries(lat: float, lon: float) -> Dict[str, Any]:
    from app.agents.geofencing_agent import GeofencingAgent
    agent = GeofencingAgent()
    return agent.process(lat, lon)

@tool_registry.register(
    name="get_lightning_risk",
    description="Retrieve convective lightning activity, proximity distance, strike density, and safety alert level",
    category="HAZARD"
)
def tool_get_lightning_risk(lat: float, lon: float) -> Dict[str, Any]:
    from app.agents.lightning_agent import LightningAgent
    agent = LightningAgent()
    return agent.process(lat, lon)

@tool_registry.register(
    name="get_cyclone_tracking",
    description="Retrieve active cyclone coordinates, track forecast, intensity, and user cone-of-uncertainty proximity",
    category="HAZARD"
)
def tool_get_cyclone_tracking(lat: float, lon: float) -> Dict[str, Any]:
    from app.agents.cyclone_agent import CycloneAgent
    agent = CycloneAgent()
    return agent.process(lat, lon)

@tool_registry.register(
    name="calculate_marine_risk",
    description="Calculate composite 0-100 marine risk (SAFE/CAUTION/DANGER) using XGBoost ML, Isolation Forest, and physics",
    category="RISK"
)
def tool_calculate_marine_risk(fused_data: Dict[str, Any], agent_findings: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    from app.risk.risk_engine import RiskEngine
    engine = RiskEngine()
    return engine.calculate_risk(fused_data, agent_findings)

@tool_registry.register(
    name="calculate_safe_route",
    description="Calculate A* risk-bypassing marine navigation routes with geofence validation and route rejection check",
    category="ROUTE"
)
def tool_calculate_safe_route(
    origin_lat: float, origin_lon: float,
    dest_lat: float, dest_lon: float,
    origin_name: str = "Origin Point",
    dest_name: str = "Destination Point"
) -> Dict[str, Any]:
    from app.gis.pathfinding import RoutePathfinder
    pathfinder = RoutePathfinder()
    return pathfinder.find_routes(origin_lat, origin_lon, dest_lat, dest_lon, origin_name, dest_name).model_dump()

@tool_registry.register(
    name="optimize_departure_windows",
    description="Analyze progressive departure time windows (e.g. 06:00, 08:00, 10:00, 12:00) and recommend safest window",
    category="ROUTE"
)
def tool_optimize_departure_windows(lat: float, lon: float, base_time: Optional[str] = None) -> Dict[str, Any]:
    from app.gis.pathfinding import RoutePathfinder
    pathfinder = RoutePathfinder()
    return pathfinder.optimize_departure_windows(lat, lon, base_time)

@tool_registry.register(
    name="get_coral_ecosystem_health",
    description="Assess Degree Heating Weeks (DHW), SST thermal stress anomaly, and coral bleaching risk",
    category="ECOSYSTEM"
)
def tool_get_coral_ecosystem_health(lat: float, lon: float, ocean_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    from app.agents.coral_agent import CoralAgent
    agent = CoralAgent()
    return agent.process(lat, lon, ocean_data)

@tool_registry.register(
    name="assess_vessel_suitability",
    description="Evaluate craft operational safety across Artisanal (<12m), Coastal (12-50m), and Commercial (>50m)",
    category="VESSEL"
)
def tool_assess_vessel_suitability(lat: float, lon: float, conditions: Dict[str, Any], vessel_class: str = "ARTISANAL") -> Dict[str, Any]:
    from app.agents.vessel_agent import VesselAgent
    agent = VesselAgent()
    return agent.process(lat, lon, conditions, vessel_class=vessel_class)

@tool_registry.register(
    name="retrieve_incois_knowledge",
    description="Retrieve official INCOIS, DG Shipping, and IMD regulatory bulletins and circulars using RAG semantic search",
    category="RAG"
)
def tool_retrieve_incois_knowledge(query: str, top_k: int = 3) -> Dict[str, Any]:
    from app.rag.rag_engine import MarineKnowledgeRAG
    return MarineKnowledgeRAG.query_knowledge(query, top_k=top_k).model_dump()
