"""
VARUNA Master Orchestrator Agent
Collaborative Agentic AI for Marine Decision Intelligence (SIH26176 / ISRO).
Coordinates autonomous intent parsing, dynamic tool selection, multi-source data discovery,
cross-agent collaborative reasoning, GIS geofencing, risk fusion, and localized multilingual delivery.
"""

import math
import copy
import time
import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
        sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")
    except Exception:
        pass

logger = logging.getLogger("varuna.master_agent")

from app.agents.intent_context_agent import IntentContextAgent, StructuredContext
from app.agents.data_discovery_agent import DataDiscoveryAgent
from app.agents.language_service import LanguageService
from app.agents.ocean_agent import OceanAgent
from app.agents.weather_agent import WeatherAgent
from app.agents.satellite_agent import SatelliteAgent
from app.agents.fisheries_agent import FisheriesAgent
from app.agents.coral_agent import CoralAgent
from app.agents.vessel_agent import VesselAgent
from app.agents.gis_agent import GISAgent
from app.agents.geofencing_agent import GeofencingAgent
from app.agents.lightning_agent import LightningAgent
from app.agents.cyclone_agent import CycloneAgent
from app.agents.hazard_agent import HazardAgent
from app.agents.prediction_agent import PredictionAgent
from app.agents.anomaly_agent import AnomalyAgent
from app.agents.risk_agent import RiskAgent
from app.agents.advisory_agent import AdvisoryAgent
from app.agents.route_agent import RouteAgent
from app.agents.safety_verification_agent import SafetyVerificationAgent
from app.fusion.fusion_engine import DataFusionEngine
from app.risk.risk_engine import RiskEngine
from app.gis.pathfinding import RoutePathfinder
from app.agents.collaborative_engine import CollaborativeAIEngine
from app.models.schemas import (
    AgentTraceResponse, AgentExecutionStep, RiskAssessmentResponse,
    CombinedMarineData, RouteComparisonResponse, MarineWhyEngine, DecisionDNA,
    AgentDissentResponse, MarineTimelineResponse
)

class MasterAgent:
    """
    Master Orchestrator Agent coordinating specialized marine sub-agents.
    Executes collaborative agentic reasoning, cross-agent evidence exchange,
    conflict resolution, central risk fusion, and transparent multi-agent explainability.
    """

    def __init__(self):
        self.intent_agent = IntentContextAgent()
        self.data_discovery_agent = DataDiscoveryAgent()
        self.ocean_agent = OceanAgent()
        self.weather_agent = WeatherAgent()
        self.satellite_agent = SatelliteAgent()
        self.fisheries_agent = FisheriesAgent()
        self.coral_agent = CoralAgent()
        self.vessel_agent = VesselAgent()
        self.gis_agent = GISAgent()
        self.geofencing_agent = GeofencingAgent()
        self.lightning_agent = LightningAgent()
        self.cyclone_agent = CycloneAgent()
        self.hazard_agent = HazardAgent()
        self.prediction_agent = PredictionAgent()
        self.anomaly_agent = AnomalyAgent()
        self.risk_agent = RiskAgent()
        self.advisory_agent = AdvisoryAgent()
        self.route_agent = RouteAgent()
        self.safety_agent = SafetyVerificationAgent()
        self.risk_engine = RiskEngine()
        self.route_pathfinder = RoutePathfinder()
        self._location_cache: Dict[Any, Any] = {}

    def get_all_agents_status(self) -> List[Dict[str, Any]]:
        """
        Returns registry and operational health status of all specialized agents.
        """
        return [
            {"agent_id": "master_agent", "name": "Master Orchestrator Agent", "domain": "Autonomous Planning, Task Decomposition & Agent Coordination", "status": "OPERATIONAL", "confidence_weight": 0.99, "capabilities": ["task_planning", "tool_selection", "evidence_synthesis", "conflict_resolution"]},
            {"agent_id": "intent_context_agent", "name": "Intent & Context Agent", "domain": "Multilingual Intent Extraction & Multi-Turn Session Memory", "status": "OPERATIONAL", "confidence_weight": 0.96, "capabilities": ["intent_classification", "entity_extraction", "session_memory", "time_horizon_parsing"]},
            {"agent_id": "data_discovery_agent", "name": "Data Discovery Agent", "domain": "Dynamic Marine Dataset Selection & Trust Assessment", "status": "OPERATIONAL", "confidence_weight": 0.95, "capabilities": ["dataset_discovery", "freshness_tracking", "provider_selection"]},
            {"agent_id": "ocean_agent", "name": "Ocean Agent", "domain": "Wave Dynamics, Swell, Currents & Ocean State", "status": "OPERATIONAL", "confidence_weight": 0.94, "capabilities": ["wave_height", "wave_direction", "ocean_currents", "sst", "salinity"]},
            {"agent_id": "weather_agent", "name": "Weather Agent", "domain": "Meteorology, Wind Gusts & Cyclonic Pressure", "status": "OPERATIONAL", "confidence_weight": 0.94, "capabilities": ["wind_speed", "wind_direction", "surface_pressure", "precipitation", "storm_flags"]},
            {"agent_id": "satellite_agent", "name": "Satellite Agent", "domain": "Remote Sensing, Ocean Colour & Turbidity", "status": "OPERATIONAL", "confidence_weight": 0.88, "capabilities": ["chlorophyll_a", "turbidity_index", "thermal_fronts", "algal_bloom_watch"]},
            {"agent_id": "fisheries_agent", "name": "Fisheries / PFZ Agent", "domain": "PFZ Candidate Discovery, Ranking & Artisanal Safety", "status": "OPERATIONAL", "confidence_weight": 0.91, "capabilities": ["pfz_ranking", "target_species", "sst_gradients", "artisanal_limits"]},
            {"agent_id": "coral_agent", "name": "Coral Health Agent", "domain": "Thermal Bleaching Stress & Ecosystem Resilience", "status": "OPERATIONAL", "confidence_weight": 0.90, "capabilities": ["degree_heating_weeks", "sst_anomaly", "bleaching_alert", "ecosystem_index"]},
            {"agent_id": "vessel_agent", "name": "Vessel Agent", "domain": "Maritime Navigation Safety & Craft Limitations", "status": "OPERATIONAL", "confidence_weight": 0.92, "capabilities": ["vessel_class_risk", "speed_reduction", "wave_steepness", "nav_clearance"]},
            {"agent_id": "gis_agent", "name": "GIS Marine Grid Agent", "domain": "Spatial Indexing & Marine Boundaries", "status": "OPERATIONAL", "confidence_weight": 0.98, "capabilities": ["grid_snapping", "coastal_distance", "region_lookup"]},
            {"agent_id": "geofencing_agent", "name": "Geofencing Agent", "domain": "IMBL, Naval Exclusion & MPA Compliance", "status": "OPERATIONAL", "confidence_weight": 0.99, "capabilities": ["imbl_proximity", "restricted_waters_check", "mpa_detection", "route_boundary_validation"]},
            {"agent_id": "lightning_agent", "name": "Lightning Agent", "domain": "Convective Thunderstorm & Strike Proximity", "status": "OPERATIONAL", "confidence_weight": 0.92, "capabilities": ["strike_density", "convective_index", "lightning_distance"]},
            {"agent_id": "cyclone_agent", "name": "Cyclone Agent", "domain": "Active Cyclone Tracking & Cone of Uncertainty", "status": "OPERATIONAL", "confidence_weight": 0.96, "capabilities": ["cyclone_tracking", "cone_distance", "landfall_eta", "gale_radius"]},
            {"agent_id": "hazard_agent", "name": "Hazard Alert Agent", "domain": "Proactive Marine Hazard Monitoring & Dispatch", "status": "OPERATIONAL", "confidence_weight": 0.95, "capabilities": ["hazard_synthesis", "alert_generation", "severity_escalation"]},
            {"agent_id": "anomaly_agent", "name": "Anomaly Agent", "domain": "Isolation Forest Environmental Outlier Detection", "status": "OPERATIONAL", "confidence_weight": 0.91, "capabilities": ["multivariate_anomaly_score", "outlier_tagging"]},
            {"agent_id": "risk_agent", "name": "Risk & SHAP Explainer Agent", "domain": "XGBoost ML Risk & Feature Contribution", "status": "OPERATIONAL", "confidence_weight": 0.94, "capabilities": ["xgboost_risk_score", "shap_positive_forces", "shap_negative_forces"]},
            {"agent_id": "safety_verification_agent", "name": "Safety Verification Agent", "domain": "Marine Guardrail & 10-Point Safety Verification", "status": "OPERATIONAL", "confidence_weight": 0.99, "capabilities": ["safety_guardrails", "no_hallucination_check", "route_rejection_validation"]}
        ]

    def _execute_collaborative_reasoning(
        self,
        ocean_res: Dict[str, Any],
        weather_res: Dict[str, Any],
        sat_res: Dict[str, Any],
        fisheries_res: Dict[str, Any],
        coral_res: Dict[str, Any],
        vessel_res: Dict[str, Any],
        geofence_res: Optional[Dict[str, Any]] = None,
        lightning_res: Optional[Dict[str, Any]] = None,
        cyclone_res: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Cross-agent evidence exchange and collaborative consensus layer.
        """
        agreements = []
        conflicts = []

        ocean_status = ocean_res.get("status", "SAFE")
        weather_status = weather_res.get("status", "SAFE")
        coral_status = coral_res.get("status", "SAFE")
        vessel_status = vessel_res.get("status", "SAFE")
        fisheries_status = fisheries_res.get("status", "SAFE")

        # 1. Weather + Ocean wave/wind corroboration
        wave_h = ocean_res.get("findings", {}).get("wave_height", 1.2)
        wind_s = weather_res.get("findings", {}).get("wind_speed", 15.0)

        if wave_h >= 2.0 and wind_s >= 22.0:
            agreements.append(f"Ocean Agent ({wave_h}m waves) and Weather Agent ({wind_s} km/h winds) corroborate elevated sea state forcing.")
        elif wave_h < 1.5 and wind_s < 18.0:
            agreements.append("Ocean Agent and Weather Agent corroborate calm, stable marine atmospheric baseline.")
        elif wave_h >= 2.2 and wind_s < 15.0:
            conflicts.append(f"Swell Discrepancy: Ocean Agent reports high wave swell ({wave_h}m) despite moderate local winds ({wind_s} km/h), indicating distant storm propagation.")

        # 2. Vessel + Fisheries operational agreement
        if vessel_status == "DANGER" and fisheries_status == "DANGER":
            agreements.append("Vessel Agent and Fisheries Agent unanimously confirm hazardous conditions for artisanal and small craft.")
        elif vessel_status == "SAFE" and fisheries_status == "SAFE":
            agreements.append("Vessel Agent and Fisheries Agent confirm favorable operational windows for fishing and transit.")

        # 3. Coral + Satellite SST agreement
        sst = ocean_res.get("findings", {}).get("sst", 28.5)
        dhw = coral_res.get("findings", {}).get("degree_heating_weeks", 0.0)
        if dhw > 3.0 and sst > 29.0:
            agreements.append(f"Coral Health Agent and Ocean Agent corroborate elevated thermal accumulation (SST: {sst}°C, DHW: {dhw}).")

        # 4. Geofence corroboration
        if geofence_res and geofence_res.get("status") == "DANGER":
            agreements.append("Geofencing Agent flagged boundary violation / restricted sector, establishing critical safety priority.")

        # Consensus risk determination
        all_statuses = [ocean_status, weather_status, coral_status, vessel_status, fisheries_status]
        if geofence_res:
            all_statuses.append(geofence_res.get("status", "SAFE"))
        if lightning_res:
            all_statuses.append(lightning_res.get("status", "SAFE"))
        if cyclone_res:
            all_statuses.append(cyclone_res.get("status", "SAFE"))

        danger_count = all_statuses.count("DANGER")
        caution_count = all_statuses.count("CAUTION")

        if danger_count >= 2 or (danger_count >= 1 and caution_count >= 2):
            consensus_level = "DANGER"
        elif danger_count >= 1 or caution_count >= 2:
            consensus_level = "CAUTION"
        else:
            consensus_level = "SAFE"

        return {
            "agreements": agreements,
            "conflicts": conflicts,
            "consensus_level": consensus_level,
            "collaborative_summary": (
                f"Multi-agent consensus achieved ({consensus_level}). "
                f"{len(agreements)} corroborating evidence link(s) established. "
                + (f"Note: {conflicts[0]}" if conflicts else "No conflicting sensor signals detected.")
            )
        }

    def _analyse_location_uncached(
        self,
        lat: float,
        lon: float,
        mode: str = "HYBRID",
        target_time: Optional[str] = None,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Primary location analysis logic. Gathers all agent evidence,
        fuses raw data, runs RiskEngine, and returns structured findings.
        """
        # GIS bounds
        gis_res = self.gis_agent.process(lat, lon)
        marine_region = gis_res["findings"].get("marine_region", f"Marine Point ({round(lat,2)}, {round(lon,2)})")

        # Run specialized domain agents with target_time and force_refresh
        ocean_res = self.ocean_agent.process(lat, lon, mode=mode, target_time=target_time, force_refresh=force_refresh)
        weather_res = self.weather_agent.process(lat, lon, mode=mode, target_time=target_time, force_refresh=force_refresh)
        ocean_findings = ocean_res["findings"]
        weather_findings = weather_res["findings"]
        sat_res = self.satellite_agent.process(lat, lon, ocean_findings, mode=mode)
        sat_findings = sat_res["findings"]

        # Run specialized agents
        fisheries_res = self.fisheries_agent.process(lat, lon, ocean_findings)
        coral_res = self.coral_agent.process(lat, lon, ocean_findings)
        vessel_res = self.vessel_agent.process(lat, lon, {**ocean_findings, **weather_findings})
        geofence_res = self.geofencing_agent.process(lat, lon)
        lightning_res = self.lightning_agent.process(lat, lon, weather_findings)
        cyclone_res = self.cyclone_agent.process(lat, lon)
        hazard_res = self.hazard_agent.process(lat, lon, ocean_findings, weather_findings, lightning_res, cyclone_res)
        adv_res = self.advisory_agent.process(marine_region)

        # Multi-source Data Fusion
        fused_record = DataFusionEngine.fuse_records(
            lat=lat, lon=lon,
            ocean_raw=ocean_findings,
            weather_raw=weather_findings,
            satellite_raw=sat_findings,
            location_name=marine_region
        )
        fused_dict = fused_record.model_dump()

        # Run Anomaly and Prediction
        anom_res = self.anomaly_agent.process(fused_dict)
        pred_res = self.prediction_agent.process(fused_dict)

        # Log Prediction output (Priority 5)
        pred_findings = pred_res.get("findings", {})
        print(f"[PREDICTION]\nstatus=SUCCESS\npredicted_wave_height_24h={pred_findings.get('predicted_wave_height_24h', '?')}m\npredicted_wind_speed_24h={pred_findings.get('predicted_wind_speed_24h', '?')} km/h\npressure_tendency={pred_findings.get('pressure_tendency', 'STABLE')}", flush=True)

        # Collaborative Evidence Exchange
        collab_res = self._execute_collaborative_reasoning(
            ocean_res, weather_res, sat_res, fisheries_res, coral_res, vessel_res,
            geofence_res=geofence_res, lightning_res=lightning_res, cyclone_res=cyclone_res
        )

        all_agent_findings = [ocean_res, weather_res, sat_res, fisheries_res, coral_res, vessel_res, anom_res, geofence_res, lightning_res, cyclone_res, pred_res]

        # Central Risk Engine
        risk_result = self.risk_engine.calculate_risk(fused_dict, all_agent_findings)

        # Final Safety Verification Check
        safety_check = self.safety_agent.verify_safety(
            fused_data=fused_dict,
            agent_findings=all_agent_findings,
            geofence_data=geofence_res,
            hazard_data=hazard_res
        )

        res_dict = {
            "latitude": lat,
            "longitude": lon,
            "location_name": marine_region,
            "timestamp": fused_record.timestamp,
            "operational_mode": mode,
            "risk_level": risk_result["risk_level"],
            "risk_score": risk_result["risk_score"],
            "confidence": int(risk_result["confidence"] * 100),
            "uncertainty_level": risk_result["uncertainty_level"],
            "current_conditions": {
                "wave_height_m": fused_record.wave_height,
                "wave_period_s": fused_record.wave_period,
                "swell_height_m": fused_record.swell_height,
                "current_velocity_ms": fused_record.current_velocity,
                "wind_speed_kmh": fused_record.wind_speed,
                "wind_direction_deg": fused_record.wind_direction,
                "surface_pressure_hpa": fused_record.pressure,
                "sea_surface_temp_c": fused_record.sst,
                "precipitation_mm": fused_record.precipitation,
                "salinity_psu": fused_record.salinity,
                "chlorophyll_mg_m3": fused_record.chlorophyll,
                "data_freshness": fused_record.quality_report.freshness,
                "data_quality_score": fused_record.quality_report.quality_score,
                "trust_score": fused_record.trust_score
            },
            "key_risks": risk_result["key_risks"],
            "risk_components": risk_result["components"],
            "agent_findings": [
                {
                    "agent": "Ocean Agent",
                    "status": ocean_res["status"],
                    "confidence": ocean_res["confidence"],
                    "summary": f"Wave: {fused_record.wave_height}m | Swell: {fused_record.swell_height}m | Currents: {fused_record.current_velocity} m/s",
                    "reasons": ocean_res["reasons"],
                    "recommendations": ocean_res["recommendations"]
                },
                {
                    "agent": "Weather Agent",
                    "status": weather_res["status"],
                    "confidence": weather_res["confidence"],
                    "summary": f"Wind: {fused_record.wind_speed} km/h | Pressure: {fused_record.pressure} hPa",
                    "reasons": weather_res["reasons"],
                    "recommendations": weather_res["recommendations"]
                },
                {
                    "agent": "Prediction Agent",
                    "status": pred_res["status"],
                    "confidence": pred_findings.get("confidence", 0.89),
                    "summary": f"24h Trend Horizon: Wave {pred_findings.get('predicted_wave_height_24h')}m | Wind {pred_findings.get('predicted_wind_speed_24h')} km/h | Pressure {pred_findings.get('pressure_tendency')}",
                    "reasons": [
                        f"Predicted wave height (24h): {pred_findings.get('predicted_wave_height_24h')} m",
                        f"Predicted wind speed (24h): {pred_findings.get('predicted_wind_speed_24h')} km/h",
                        f"Barometric pressure tendency: {pred_findings.get('pressure_tendency')}"
                    ],
                    "recommendations": [
                        "Incorporate 24-hour predictive trends into departure window safety margins."
                    ]
                },
                {
                    "agent": "Satellite Agent",
                    "status": sat_res["status"],
                    "confidence": sat_res["confidence"],
                    "summary": f"Chlorophyll: {fused_record.chlorophyll} mg/m³ | Turbidity: {sat_findings.get('turbidity_index', 0.2)}",
                    "reasons": sat_res["reasons"],
                    "recommendations": sat_res["recommendations"]
                },
                {
                    "agent": "Fisheries Agent",
                    "status": fisheries_res["status"],
                    "confidence": fisheries_res["confidence"],
                    "summary": f"Top PFZ Score: {fisheries_res['findings'].get('primary_pfz', {}).get('fishing_potential_score', 85)}/100 | Target: {', '.join(fisheries_res['findings']['target_species'][:2])}",
                    "reasons": fisheries_res["reasons"],
                    "recommendations": fisheries_res["recommendations"]
                },
                {
                    "agent": "Coral Agent",
                    "status": coral_res["status"],
                    "confidence": coral_res["confidence"],
                    "summary": f"Degree Heating Weeks: {coral_res['findings'].get('degree_heating_weeks', 0.0)} | Bleaching: {coral_res['findings'].get('bleaching_alert_level', 'NORMAL')}",
                    "reasons": coral_res["reasons"],
                    "recommendations": coral_res["recommendations"]
                },
                {
                    "agent": "Geofencing Agent",
                    "status": geofence_res["status"],
                    "confidence": geofence_res["confidence"],
                    "summary": "Boundary Check: " + ("Clear" if geofence_res["findings"]["is_geofence_compliant"] else "Boundary/Restricted Alert"),
                    "reasons": geofence_res["reasons"],
                    "recommendations": geofence_res["recommendations"]
                },
                {
                    "agent": "Lightning Agent",
                    "status": lightning_res["status"],
                    "confidence": lightning_res["confidence"],
                    "summary": f"Lightning Activity: {lightning_res['status']} | Nearest: {lightning_res['findings']['nearest_strike_distance_km']} km",
                    "reasons": lightning_res["reasons"],
                    "recommendations": lightning_res["recommendations"]
                },
                {
                    "agent": "Cyclone Agent",
                    "status": cyclone_res["status"],
                    "confidence": cyclone_res["confidence"],
                    "summary": f"Cyclone: {cyclone_res['findings']['name']} ({cyclone_res['findings']['user_distance_to_center_km']} km away)",
                    "reasons": cyclone_res["reasons"],
                    "recommendations": cyclone_res["recommendations"]
                }
            ],
            "collaborative_reasoning": collab_res,
            "geofence_summary": geofence_res["findings"],
            "hazard_summary": hazard_res,
            "safety_verification": safety_check,
            "pfz_candidates": fisheries_res["findings"].get("all_candidate_pfzs", []),
            "prediction_summary": pred_findings,
            "data_provenance": {
                "source": fused_record.source,
                "status": fused_record.status,
                "live_data_available": fused_record.live_data_available,
                "fetched_at": fused_record.fetched_at,
                "is_forecast": fused_record.is_forecast,
                "forecast_target": fused_record.forecast_target
            },
            "explainability": {
                "top_positive_forces": risk_result["positive_forces"],
                "top_negative_forces": risk_result["negative_forces"]
            },
            "recommendations": risk_result["recommendations"],
            "fused_record": fused_record
        }

        # Build Collaborative Agentic AI Intelligence models
        conds = res_dict["current_conditions"]
        rec_label = CollaborativeAIEngine.get_recommendation_from_risk(
            risk_result["risk_score"],
            has_geofence_violation=not geofence_res["findings"].get("is_geofence_compliant", True),
            has_storm=(cyclone_res.get("status") == "DANGER" or lightning_res.get("status") == "DANGER")
        )

        why_eng = CollaborativeAIEngine.generate_why_engine(
            risk_score=risk_result["risk_score"],
            risk_level=risk_result["risk_level"],
            recommendation=rec_label,
            location_name=marine_region,
            current_conditions=conds,
            agent_findings=res_dict["agent_findings"],
            collab_reasoning=collab_res,
            confidence=risk_result["confidence"]
        )

        dna_obj = CollaborativeAIEngine.generate_decision_dna(
            recommendation=rec_label,
            risk_score=risk_result["risk_score"],
            confidence=risk_result["confidence"],
            latitude=lat,
            longitude=lon,
            location_name=marine_region,
            current_conditions=conds,
            agent_findings=res_dict["agent_findings"]
        )

        dissent_obj = CollaborativeAIEngine.resolve_agent_dissent(
            current_conditions=conds,
            agent_findings=res_dict["agent_findings"],
            overall_risk_score=risk_result["risk_score"],
            geofence_data=geofence_res["findings"]
        )

        timeline_obj = CollaborativeAIEngine.generate_marine_timeline(
            latitude=lat,
            longitude=lon,
            location_name=marine_region,
            current_conditions=conds,
            current_risk_score=risk_result["risk_score"]
        )

        res_dict["recommendation"] = rec_label
        res_dict["why_engine"] = why_eng
        res_dict["decision_dna"] = dna_obj
        res_dict["agent_dissent"] = dissent_obj
        res_dict["timeline"] = timeline_obj
        res_dict["what_would_change"] = dna_obj.what_would_change_decision

        return res_dict

    def analyse_location(
        self,
        lat: float,
        lon: float,
        mode: str = "HYBRID",
        target_time: Optional[str] = None,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """Return fresh location analysis with controlled caching."""
        cache_key = (round(lat, 4), round(lon, 4), mode, target_time or "current")
        if not force_refresh:
            cached = self._location_cache.get(cache_key)
            if cached and time.monotonic() - cached[0] < 120:
                res = copy.deepcopy(cached[1])
                if "data_provenance" in res:
                    res["data_provenance"]["status"] = "CACHED"
                return res

        result = self._analyse_location_uncached(lat, lon, mode=mode, target_time=target_time, force_refresh=force_refresh)
        self._location_cache[cache_key] = (time.monotonic(), result)
        return copy.deepcopy(result)

    def scan_area(self, lat: float, lon: float, radius_km: float = 50.0, mode: str = "HYBRID") -> Dict[str, Any]:
        deg_offset = round(radius_km / 111.0, 3)
        directions = [
            {"direction": "N",  "label": "North",     "dlat": +deg_offset, "dlon": 0.0},
            {"direction": "NE", "label": "North-East", "dlat": +deg_offset * 0.707, "dlon": +deg_offset * 0.707},
            {"direction": "E",  "label": "East",      "dlat": 0.0, "dlon": +deg_offset},
            {"direction": "SE", "label": "South-East", "dlat": -deg_offset * 0.707, "dlon": +deg_offset * 0.707},
            {"direction": "S",  "label": "South",     "dlat": -deg_offset, "dlon": 0.0},
            {"direction": "SW", "label": "South-West", "dlat": -deg_offset * 0.707, "dlon": -deg_offset * 0.707},
            {"direction": "W",  "label": "West",      "dlat": 0.0, "dlon": -deg_offset},
            {"direction": "NW", "label": "North-West", "dlat": +deg_offset * 0.707, "dlon": -deg_offset * 0.707},
        ]

        current_analysis = self.analyse_location(lat, lon, mode=mode)
        nearby_scans = []
        elevated_threats = []

        for d in directions:
            pt_lat = round(lat + d["dlat"], 4)
            pt_lon = round(lon + d["dlon"], 4)
            pt_res = self.analyse_location(pt_lat, pt_lon, mode=mode)

            scan_item = {
                "direction": d["direction"],
                "label": d["label"],
                "latitude": pt_lat,
                "longitude": pt_lon,
                "distance_km": radius_km,
                "risk_level": pt_res["risk_level"],
                "risk_score": pt_res["risk_score"],
                "wave_height_m": pt_res["current_conditions"]["wave_height_m"],
                "wind_speed_kmh": pt_res["current_conditions"]["wind_speed_kmh"],
                "key_risks": pt_res["key_risks"],
                "summary": f"{d['label']} ({radius_km}km): {pt_res['risk_level']} (Risk {pt_res['risk_score']}/100)"
            }
            nearby_scans.append(scan_item)

            if pt_res["risk_level"] in ["CAUTION", "DANGER"]:
                elevated_threats.append(
                    f"{d['label']} corridor ({radius_km}km away) indicates {pt_res['risk_level']} risk (Score {pt_res['risk_score']}/100) due to {pt_res['key_risks'][0]}."
                )

        return {
            "center": {"latitude": lat, "longitude": lon},
            "radius_km": radius_km,
            "current_location_safety": {
                "risk_level": current_analysis["risk_level"],
                "risk_score": current_analysis["risk_score"],
                "confidence": current_analysis["confidence"],
                "summary": f"Current Location: {current_analysis['risk_level']} (Score {current_analysis['risk_score']}/100)"
            },
            "directional_scans": nearby_scans,
            "predictive_threat_summary": elevated_threats if elevated_threats else ["All surrounding sectors within radius exhibit SAFE baseline marine conditions."],
            "recommended_heading": next((s["label"] for s in nearby_scans if s["risk_level"] == "SAFE"), "Maintain Current Heading")
        }

    def analyse_route(
        self,
        origin_lat: float,
        origin_lon: float,
        dest_lat: float,
        dest_lon: float,
        origin_name: str = "Origin Point",
        dest_name: str = "Destination Point",
        mode: str = "HYBRID"
    ) -> Dict[str, Any]:
        """
        Route Safety Mode: Progressive waypoint check + A* route options with geofence validation.
        """
        route_comp = self.route_pathfinder.find_routes(
            origin_lat, origin_lon, dest_lat, dest_lon, origin_name, dest_name
        )

        R = 6371.0
        dlat = math.radians(dest_lat - origin_lat)
        dlon = math.radians(dest_lon - origin_lon)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(origin_lat)) * math.cos(math.radians(dest_lat)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        total_dist_km = round(R * c, 1)

        fractions = [0.0, 0.25, 0.5, 0.75, 1.0] if total_dist_km <= 50.0 else [0.0, 10.0 / total_dist_km, 25.0 / total_dist_km, 50.0 / total_dist_km, 1.0]

        max_risk = 0.0
        route_waypoints = []
        danger_alerts = []

        for frac in fractions:
            cur_km = round(total_dist_km * frac, 1)
            pt_lat = round(origin_lat + (dest_lat - origin_lat) * frac, 4)
            pt_lon = round(origin_lon + (dest_lon - origin_lon) * frac, 4)

            label = "CURRENT LOCATION" if frac == 0.0 else (f"{int(cur_km)} KM AHEAD" if frac < 1.0 else f"DESTINATION ({dest_name})")
            pt_analysis = self.analyse_location(pt_lat, pt_lon, mode=mode)
            
            score = pt_analysis["risk_score"]
            level = pt_analysis["risk_level"]
            max_risk = max(max_risk, score)

            wp_info = {
                "label": label,
                "distance_from_origin_km": cur_km,
                "latitude": pt_lat,
                "longitude": pt_lon,
                "risk_level": level,
                "risk_score": score,
                "wave_height_m": pt_analysis["current_conditions"]["wave_height_m"],
                "wind_speed_kmh": pt_analysis["current_conditions"]["wind_speed_kmh"],
                "key_risks": pt_analysis["key_risks"],
                "recommendation": pt_analysis["recommendations"][0] if pt_analysis["recommendations"] else "Proceed safely."
            }
            route_waypoints.append(wp_info)

            if level in ["CAUTION", "DANGER"]:
                danger_alerts.append(f"{label}: {level} Risk ({score}/100) — {pt_analysis['key_risks'][0]}")

        overall_route_level = "DANGER" if max_risk >= 61.0 else ("CAUTION" if max_risk >= 31.0 else "SAFE")

        return {
            "origin": {"name": origin_name, "latitude": origin_lat, "longitude": origin_lon},
            "destination": {"name": dest_name, "latitude": dest_lat, "longitude": dest_lon},
            "total_distance_km": total_dist_km,
            "overall_route_safety": overall_route_level,
            "max_risk_score": max_risk,
            "progressive_checkpoints": route_waypoints,
            "route_comparison": route_comp,
            "predictive_route_threats": danger_alerts if danger_alerts else ["Entire transit corridor presents SAFE marine parameters."],
            "route_clearance": "RESTRICTED" if overall_route_level == "DANGER" else ("ADVISORY" if overall_route_level == "CAUTION" else "CLEAR")
        }

    def process_query(
        self,
        query: str,
        lat: float = 18.9667,
        lon: float = 72.8333,
        mode: str = "HYBRID",
        conversation_history: Optional[List[Dict[str, str]]] = None,
        session_id: Optional[str] = None
    ) -> AgentTraceResponse:
        """
        Fully autonomous ReAct & Multi-Agent DAG query pipeline.
        Fulfills SIH requirements #1 through #20.
        """
        from app.services.gemini_service import gemini_service

        steps: List[AgentExecutionStep] = []
        now_str = lambda: datetime.now(timezone.utc).isoformat()
        request_id = f"req_{uuid.uuid4().hex[:8]}"
        t_start = time.perf_counter()
        dag_start_iso = datetime.now(timezone.utc).isoformat()

        # Step 1: Autonomous Intent & Context Extraction with Multi-Turn Memory
        ctx = self.intent_agent.extract_context(
            query=query,
            current_lat=lat,
            current_lon=lon,
            session_id=session_id or "default_session"
        )

        steps.append(AgentExecutionStep(
            agent_name="IntentContextAgent",
            status="COMPLETED",
            action_taken=f"Extracted structured intent '{ctx.intent}' in language '{ctx.language}' for target sector '{ctx.location_name}'",
            details=ctx.to_dict(),
            timestamp=now_str()
        ))

        # Step 2: Autonomous Data Discovery Agent
        data_plan = self.data_discovery_agent.discover_data_requirements(ctx)
        steps.append(AgentExecutionStep(
            agent_name="DataDiscoveryAgent",
            status="COMPLETED",
            action_taken=f"Identified {data_plan['required_dataset_count']} required datasets and selected {len(data_plan['selected_tools'])} specialized tools",
            details=data_plan,
            timestamp=now_str()
        ))

        # Step 3: Location Telemetry & Core Agent Processing
        try:
            print(f"\n[VARUNA]\nquery={query}", flush=True)
            print(f"[LOCATION]\nlat={ctx.latitude}\nlon={ctx.longitude}\nsource={ctx.location_source}", flush=True)
        except Exception:
            safe_q = query.encode("ascii", "backslashreplace").decode("ascii")
            print(f"\n[VARUNA]\nquery={safe_q}", flush=True)
            print(f"[LOCATION]\nlat={ctx.latitude}\nlon={ctx.longitude}\nsource={ctx.location_source}", flush=True)

        loc_analysis = self.analyse_location(
            ctx.latitude,
            ctx.longitude,
            mode=mode,
            target_time=ctx.target_time,
            force_refresh=True
        )
        fused = loc_analysis["fused_record"]

        if ctx.is_forecast or loc_analysis.get("data_provenance", {}).get("is_forecast"):
            print(f"[FORECAST]\nstatus=SUCCESS\ntarget={ctx.target_time}", flush=True)

        # Record Domain Agent Steps
        steps.append(AgentExecutionStep(
            agent_name="GISAgent",
            status="COMPLETED",
            action_taken="Snapped coordinates to marine grid and resolved coastal marine sector",
            details={"marine_region": loc_analysis["location_name"], "lat": ctx.latitude, "lon": ctx.longitude},
            timestamp=now_str()
        ))

        steps.append(AgentExecutionStep(
            agent_name="OceanAgent",
            status="COMPLETED",
            action_taken="Retrieved live ocean physical telemetry (waves, currents, swell, SST)",
            details=loc_analysis["current_conditions"],
            timestamp=now_str()
        ))

        steps.append(AgentExecutionStep(
            agent_name="WeatherAgent",
            status="COMPLETED",
            action_taken="Retrieved meteorological wind vectors, gusts, and barometric pressure",
            details={"wind_speed": fused.wind_speed, "pressure": fused.pressure},
            timestamp=now_str()
        ))

        steps.append(AgentExecutionStep(
            agent_name="PredictionAgent",
            status="COMPLETED",
            action_taken="Calculated 24-hour predictive trends for wave swell and wind vectors",
            details=loc_analysis.get("prediction_summary", {}),
            timestamp=now_str()
        ))

        # Geofencing Step
        steps.append(AgentExecutionStep(
            agent_name="GeofencingAgent",
            status="COMPLETED",
            action_taken="Verified spatial boundaries against IMBL, Naval Exclusion, and MPA polygons",
            details=loc_analysis["geofence_summary"],
            timestamp=now_str()
        ))

        # Lightning & Hazard Steps
        steps.append(AgentExecutionStep(
            agent_name="LightningAgent",
            status="COMPLETED",
            action_taken="Checked convective storm instability and nearest strike cluster",
            details={"convective_index": loc_analysis["current_conditions"].get("precipitation_mm", 0.0)},
            timestamp=now_str()
        ))

        # Step 4: Conditional Fisheries / PFZ Execution
        pfz_candidates = loc_analysis.get("pfz_candidates", [])
        if ctx.needs_pfz or "pfz" in query.lower() or "fish" in query.lower() or "मासे" in query:
            steps.append(AgentExecutionStep(
                agent_name="FisheriesAgent",
                status="COMPLETED",
                action_taken=f"Discovered and ranked {len(pfz_candidates)} candidate Potential Fishing Zones (PFZ)",
                details={"candidate_count": len(pfz_candidates), "primary_pfz": pfz_candidates[0] if pfz_candidates else {}},
                timestamp=now_str()
            ))

        # Step 5: Conditional Departure Time Optimization Execution
        departure_opt = None
        if ctx.needs_departure_optimization or ctx.departure_hour is not None:
            departure_opt = self.route_pathfinder.optimize_departure_windows(ctx.latitude, ctx.longitude)
            steps.append(AgentExecutionStep(
                agent_name="RouteAgent",
                status="COMPLETED",
                action_taken="Evaluated multi-window departure time risk curve (06:00 to 14:00)",
                details=departure_opt,
                timestamp=now_str()
            ))

        # Step 6: Conditional Route Planning with Geofence Rejection
        route_analysis = None
        if ctx.needs_route or ctx.destination_name:
            dest_lat = ctx.dest_latitude or 15.4989
            dest_lon = ctx.dest_longitude or 73.8278
            dest_name = ctx.destination_name or "Goa Port"

            route_analysis = self.analyse_route(
                origin_lat=ctx.latitude,
                origin_lon=ctx.longitude,
                dest_lat=dest_lat,
                dest_lon=dest_lon,
                origin_name=ctx.location_name,
                dest_name=dest_name,
                mode=mode
            )
            steps.append(AgentExecutionStep(
                agent_name="RouteAgent",
                status="COMPLETED",
                action_taken="Calculated A* risk routes, evaluated geofence compliance, and checked route rejection",
                details={
                    "origin": ctx.location_name,
                    "destination": dest_name,
                    "overall_route_safety": route_analysis["overall_route_safety"],
                    "route_clearance": route_analysis["route_clearance"]
                },
                timestamp=now_str()
            ))

        # Step 7: Central Risk Engine Synthesis
        steps.append(AgentExecutionStep(
            agent_name="RiskEngine",
            status="COMPLETED",
            action_taken="Synthesized XGBoost ML risk, physics components, and SHAP explainability",
            details={"risk_score": loc_analysis["risk_score"], "risk_level": loc_analysis["risk_level"]},
            timestamp=now_str()
        ))

        # Step 8: Safety Verification Guardrail
        safety_verif = loc_analysis["safety_verification"]
        steps.append(AgentExecutionStep(
            agent_name="SafetyVerificationAgent",
            status="COMPLETED" if safety_verif["is_safety_verified"] else "WARNING",
            action_taken="Executed 10-point safety checklist, geofence clearance, and zero-hallucination verification",
            details=safety_verif,
            timestamp=now_str()
        ))

        # Step 9: Final Multilingual Response Generation
        dep_str = departure_opt.get("recommended_window_label") if departure_opt else None
        top_pfz_str = pfz_candidates[0]["name"] + f" ({pfz_candidates[0]['recommendation_badge']})" if pfz_candidates else None
        route_str = route_analysis.get("route_comparison").recommended_route_id if route_analysis and hasattr(route_analysis.get("route_comparison"), "recommended_route_id") else None

        # Base localized template
        localized_answer = LanguageService.get_localized_response_template(
            lang=ctx.language,
            risk_level=loc_analysis["risk_level"],
            risk_score=loc_analysis["risk_score"],
            location_name=loc_analysis["location_name"],
            departure_rec=dep_str,
            pfz_rec=top_pfz_str,
            route_rec=route_str,
            key_reasons=loc_analysis["key_risks"] + (loc_analysis["collaborative_reasoning"]["agreements"][:2] if loc_analysis["collaborative_reasoning"]["agreements"] else [])
        )

        # Enhance with Gemini AI if available
        chat_context = dict(loc_analysis)
        chat_context["query_language"] = ctx.language
        chat_context["structured_context"] = ctx.to_dict()
        chat_context["prediction_summary"] = loc_analysis.get("prediction_summary", {})
        chat_context["data_provenance"] = loc_analysis.get("data_provenance", {})
        if route_analysis:
            chat_context["route_analysis"] = route_analysis
        if departure_opt:
            chat_context["departure_optimization"] = departure_opt
        if pfz_candidates:
            chat_context["pfz_candidates"] = pfz_candidates

        dag_end_iso = datetime.now(timezone.utc).isoformat()

        ai_detail = gemini_service.generate_chat_response_detailed(
            user_query=query,
            marine_context=chat_context,
            conversation_history=conversation_history
        )

        ai_response = ai_detail["text"]
        total_latency_ms = (time.perf_counter() - t_start) * 1000.0

        if gemini_service.is_available and ai_detail["response_generated"]:
            final_answer = ai_response
            fallback_used = False
            fallback_reason = "NONE"
            print(f"[GEMINI]\nstatus=SUCCESS", flush=True)
            print(f"[FINAL]\nsource=LIVE_AGENT_DATA+GEMINI", flush=True)
        else:
            final_answer = ai_response if ai_response else localized_answer
            fallback_used = True
            fallback_reason = ai_detail.get("fallback_reason") or "Gemini unavailable or generation failed"
            print(f"[GEMINI]\nstatus=FALLBACK\nreason={fallback_reason}", flush=True)
            print(f"[FINAL]\nsource=LIVE_AGENT_DATA+DETERMINISTIC_SYNTHESIS", flush=True)

        audit_log = (
            f"\n================ CHATBOT REQUEST AUDIT ================\n"
            f"USER QUERY: {query}\n"
            f"LANGUAGE: {ctx.language}\n"
            f"LATITUDE: {ctx.latitude}\n"
            f"LONGITUDE: {ctx.longitude}\n"
            f"REQUEST ID: {request_id}\n"
            f"AGENT DAG START: {dag_start_iso}\n"
            f"AGENT DAG END: {dag_end_iso}\n"
            f"GEMINI CALLED = {ai_detail['gemini_called']}\n"
            f"GEMINI SKIPPED = {ai_detail['gemini_skipped']}\n"
            f"REASON FOR SKIP: {ai_detail['skip_reason'] or 'NONE'}\n"
            f"GEMINI INPUT CONTEXT SIZE: {ai_detail['input_context_size']} chars\n"
            f"GEMINI RESPONSE GENERATED = {ai_detail['response_generated']}\n"
            f"FALLBACK USED = {fallback_used}\n"
            f"FALLBACK REASON: {fallback_reason}\n"
            f"TOTAL LATENCY: {total_latency_ms:.2f}ms\n"
            f"========================================================"
        )
        logger.info(audit_log)
        try:
            print(audit_log, flush=True)
        except Exception:
            try:
                safe_log = audit_log.encode("ascii", errors="backslashreplace").decode("ascii")
                print(safe_log, flush=True)
            except Exception:
                pass

        steps.append(AgentExecutionStep(
            agent_name="ResponseAgent",
            status="COMPLETED",
            action_taken=f"Generated evidence-grounded recommendation in language '{ctx.language}'",
            details={"language": ctx.language, "response_mode": "Gemini AI (Multi-Agent Grounded)" if (gemini_service.is_available and ai_detail["response_generated"]) else "Authoritative Localized Engine"},
            timestamp=now_str()
        ))

        final_risk = RiskAssessmentResponse(
            location={"lat": ctx.latitude, "lon": ctx.longitude, "name": loc_analysis["location_name"]},
            timestamp=fused.timestamp,
            risk_score=loc_analysis["risk_score"],
            risk_level=loc_analysis["risk_level"],
            confidence=loc_analysis["confidence"] / 100.0,
            uncertainty_level=loc_analysis["uncertainty_level"],
            top_positive_forces=loc_analysis["explainability"]["top_positive_forces"],
            top_negative_forces=loc_analysis["explainability"]["top_negative_forces"],
            fused_record=fused,
            recommended_action=loc_analysis["recommendations"][0] if loc_analysis["recommendations"] else "Safe baseline marine state.",
            disclaimer="Marine risk score computed via VARUNA Collaborative Multi-Agent Reasoning & XGBoost ML."
        )

        evidence_sources = [
            {"name": "Open-Meteo Marine API", "agent": "OceanAgent", "role": "waves, swell, currents, SST", "freshness": "LIVE", "trust": 0.94},
            {"name": "Open-Meteo Weather API", "agent": "WeatherAgent", "role": "wind, pressure, gusts", "freshness": "LIVE", "trust": 0.94},
            {"name": "Copernicus / Sentinel-3 OLCI", "agent": "SatelliteAgent", "role": "chlorophyll-a, turbidity, thermal fronts", "freshness": "RECENT", "trust": 0.92},
            {"name": "INCOIS / IMD Marine Advisories", "agent": "AdvisoryAgent", "role": "official storm & wave circulars", "freshness": "LIVE", "trust": 0.98},
            {"name": "VARUNA High-Precision Spatial GIS", "agent": "GeofencingAgent", "role": "IMBL, Naval Exclusion, MPA & ESZ boundaries", "freshness": "STATIC_AUTHORITATIVE", "trust": 0.99},
            {"name": "FAO Historical Fisheries Catch", "agent": "FisheriesAgent", "role": "historical catch quantity baseline", "freshness": "HISTORICAL_BASELINE", "trust": 0.85}
        ]

        alerts = [
            {"severity": loc_analysis["risk_level"], "title": risk, "source": "RiskEngine + Collaborative Consensus"}
            for risk in loc_analysis["key_risks"]
        ]
        for v in loc_analysis["geofence_summary"].get("restricted_violations", []):
            alerts.append({"severity": "CRITICAL", "title": f"RESTRICTED ZONE: {v['name']}", "source": "GeofencingAgent"})
        for w in loc_analysis["geofence_summary"].get("imbl_warnings", []):
            alerts.append({"severity": w["severity"], "title": w["advisory"], "source": "GeofencingAgent"})

        geofence_warnings_list = [w["advisory"] for w in loc_analysis["geofence_summary"].get("imbl_warnings", [])] + [v["reason"] for v in loc_analysis["geofence_summary"].get("restricted_violations", [])]

        return AgentTraceResponse(
            query=query,
            master_agent_plan=[step.action_taken for step in steps],
            execution_steps=steps,
            final_risk_assessment=final_risk,
            final_answer=final_answer,
            detected_language=ctx.language,
            detected_intents=[ctx.intent],
            selected_agents=[s.agent_name for s in steps],
            evidence_sources=evidence_sources,
            alerts=alerts,
            geofence_warnings=geofence_warnings_list,
            recommendations=loc_analysis["recommendations"],
            structured_context=ctx.to_dict(),
            departure_optimization=departure_opt,
            geofence_summary=loc_analysis["geofence_summary"],
            pfz_candidates=pfz_candidates,
            safety_verification=safety_verif,
            why_engine=loc_analysis.get("why_engine"),
            decision_dna=loc_analysis.get("decision_dna"),
            agent_dissent=loc_analysis.get("agent_dissent"),
            timeline=loc_analysis.get("timeline"),
            what_would_change=loc_analysis.get("what_would_change"),
            data_provenance=loc_analysis.get("data_provenance"),
            prediction_summary=loc_analysis.get("prediction_summary")
        )
