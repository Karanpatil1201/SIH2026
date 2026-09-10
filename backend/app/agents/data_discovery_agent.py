"""
VARUNA Marine Data Discovery Agent
Identifies required datasets, data sources, authority levels, and freshness requirements
dynamically per user intent. Fulfills SIH Requirement #7.
"""

from typing import Dict, Any, List
from app.agents.intent_context_agent import StructuredContext

class DataDiscoveryAgent:
    """
    Data Discovery Agent dynamically selecting dataset sources and measuring freshness trust.
    """

    def __init__(self):
        self.name = "Marine Data Discovery Agent"

    def discover_data_requirements(self, ctx: StructuredContext) -> Dict[str, Any]:
        """
        Determines the minimal sufficient set of datasets and providers to query for the given context.
        """
        required_datasets: List[Dict[str, Any]] = []
        tools_to_invoke: List[str] = []

        # 1. Location & Ocean Physics
        if ctx.needs_ocean:
            required_datasets.append({
                "dataset_id": "OPEN_METEO_MARINE",
                "name": "Live Ocean Waves, Currents & SST",
                "provider": "Open-Meteo Marine API / Copernicus Marine",
                "variables": ["wave_height", "wave_period", "wave_direction", "swell_height", "current_velocity", "sst", "salinity"],
                "freshness_expected": "LIVE",
                "authority_weight": 0.94
            })
            tools_to_invoke.append("get_ocean_forecast")

        # 2. Atmospheric Weather
        if ctx.needs_weather:
            required_datasets.append({
                "dataset_id": "OPEN_METEO_WEATHER",
                "name": "Atmospheric Marine Meteorology",
                "provider": "Open-Meteo Weather API",
                "variables": ["wind_speed", "wind_gusts", "surface_pressure", "precipitation"],
                "freshness_expected": "LIVE",
                "authority_weight": 0.94
            })
            tools_to_invoke.append("get_weather_forecast")

        # 3. Satellite Remote Sensing (Chlorophyll / Turbidity)
        if ctx.needs_satellite or ctx.needs_pfz or ctx.needs_ecosystem_reasoning:
            required_datasets.append({
                "dataset_id": "SENTINEL3_OLCI_COP",
                "name": "Ocean Colour & Chlorophyll-a Fronts",
                "provider": "Copernicus Marine Service / Sentinel-3 OLCI",
                "variables": ["chlorophyll_a", "turbidity_index", "thermal_fronts"],
                "freshness_expected": "RECENT",
                "authority_weight": 0.88
            })
            tools_to_invoke.append("get_satellite_indicators")

        # 4. Fisheries & PFZ Candidates
        if ctx.needs_pfz:
            required_datasets.append({
                "dataset_id": "INCOIS_PFZ_ADVISORY",
                "name": "Potential Fishing Zones & Artisanal Safety",
                "provider": "INCOIS / FAO Historical Catch Base",
                "variables": ["pfz_indicator", "upwelling_gradient", "target_species", "catch_estimation"],
                "freshness_expected": "RECENT",
                "authority_weight": 0.92
            })
            tools_to_invoke.append("get_pfz_candidates")

        # 5. Geofencing & Marine Boundaries
        if ctx.needs_geofence_check:
            required_datasets.append({
                "dataset_id": "GIS_MARINE_BOUNDARIES",
                "name": "IMBL, Naval Exclusion & MPA Polygons",
                "provider": "VARUNA High-Precision Spatial GIS",
                "variables": ["imbl_polylines", "restricted_polygons", "mpa_polygons", "esz_polygons"],
                "freshness_expected": "STATIC_AUTHORITATIVE",
                "authority_weight": 0.99
            })
            tools_to_invoke.append("check_geofence_and_boundaries")

        # 6. Hazards (Lightning & Cyclone)
        if ctx.needs_hazard_check:
            required_datasets.append({
                "dataset_id": "LIGHTNING_AND_CYCLONE_HAZARDS",
                "name": "Convective Lightning & Cyclone Forecast Tracks",
                "provider": "IMD Marine Weather / INCOIS Bulletins",
                "variables": ["strike_density", "cyclone_cone", "central_pressure", "max_wind_knots"],
                "freshness_expected": "LIVE",
                "authority_weight": 0.95
            })
            tools_to_invoke.extend(["get_lightning_risk", "get_cyclone_tracking"])

        # 7. Route Optimization
        if ctx.needs_route:
            tools_to_invoke.append("calculate_safe_route")

        # 8. Departure Time Optimization
        if ctx.needs_departure_optimization:
            tools_to_invoke.append("optimize_departure_windows")

        # 9. Ecosystem Reasoning
        if ctx.needs_ecosystem_reasoning:
            required_datasets.append({
                "dataset_id": "HISTORICAL_ECOSYSTEM_DATASET",
                "name": "Historical Reef Bleaching, pH & SST Baselines",
                "provider": "Realistic Ocean Climate & FAO Catch Datasets",
                "variables": ["baseline_sst", "baseline_ph", "bleaching_status", "species_richness"],
                "freshness_expected": "HISTORICAL_BASELINE",
                "authority_weight": 0.85
            })
            tools_to_invoke.append("get_coral_ecosystem_health")

        return {
            "agent": self.name,
            "status": "COMPLETED",
            "intent": ctx.intent,
            "required_dataset_count": len(required_datasets),
            "discovered_datasets": required_datasets,
            "selected_tools": tools_to_invoke,
            "summary": f"Discovered {len(required_datasets)} target datasets and selected {len(tools_to_invoke)} specialized tools for intent '{ctx.intent}'."
        }
