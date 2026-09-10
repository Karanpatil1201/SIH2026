from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Optional, Any
from datetime import datetime

# User & Auth
class UserBase(BaseModel):
    username: str
    email: str
    role: str = "Fisherman"
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_active: bool
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class LoginRequest(BaseModel):
    username: str
    password: str

class OTPRequest(BaseModel):
    email: str

class OTPVerifyRequest(BaseModel):
    email: str
    otp: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")

# Data Quality & Trust
class DataQualityReport(BaseModel):
    quality_score: float = 100.0
    status: str = "VALID" # VALID, WARNING, INVALID
    missing_fields: List[str] = []
    anomalies: List[str] = []
    freshness: str = "LIVE" # LIVE, DELAYED, STALE, DEMO
    issues: List[str] = []

class ProvenanceMetadata(BaseModel):
    source: str
    dataset: str
    timestamp: str
    location: Dict[str, float]
    processing_step: str
    quality_score: float
    trust_score: float
    freshness: str
    confidence: float

# Marine Grid & Data Fusion
class CombinedMarineData(BaseModel):
    location: Dict[str, Any] # lat, lon, name
    timestamp: str
    sst: float
    wave_height: float
    wave_direction: float
    wave_period: float
    swell_height: float
    current_velocity: float
    wind_speed: float
    wind_direction: float
    pressure: float
    precipitation: float
    salinity: float
    chlorophyll: float
    sea_level: float
    quality_report: DataQualityReport
    trust_score: float
    data_source_mode: str = "LIVE" # LIVE vs DEMO vs FALLBACK
    salinity_source: str = "fallback"
    chlorophyll_source: str = "fallback"

# Risk & SHAP Explainer
class FeatureContribution(BaseModel):
    feature: str
    impact: float
    value: Any
    description: str

class RiskAssessmentResponse(BaseModel):
    location: Dict[str, Any]
    timestamp: str
    risk_score: float # 0 - 100
    risk_level: str # SAFE, CAUTION, DANGER / LOW, MODERATE, HIGH, CRITICAL
    confidence: float # 0.0 - 1.0
    uncertainty_level: str # Low, Moderate, High
    top_positive_forces: List[FeatureContribution]
    top_negative_forces: List[FeatureContribution]
    fused_record: CombinedMarineData
    recommended_action: str
    disclaimer: str

# Anomaly Detection
class AnomalyEvent(BaseModel):
    event_id: str
    event_type: str
    location: Dict[str, Any]
    severity: str
    detected_at: str
    confidence: float
    evidence: List[str]

# Route Intelligence
class RoutePoint(BaseModel):
    lat: float
    lon: float
    risk_score: float
    wave_height: float
    wind_speed: float

class RouteOption(BaseModel):
    route_id: str
    name: str # Safest Route, Fastest Route, Balanced Route
    waypoints: List[RoutePoint]
    total_distance_km: float
    estimated_time_hours: float
    average_risk_score: float
    max_wave_height: float
    max_wind_speed: float
    storm_exposure_pct: float
    advisory_count: int
    is_geofence_compliant: bool = True
    is_rejected: bool = False
    rejection_reason: Optional[str] = None
    geofence_violations: List[str] = []
    geofence_warnings: List[str] = []

class RouteComparisonResponse(BaseModel):
    origin: Dict[str, Any]
    destination: Dict[str, Any]
    routes: List[RouteOption]
    recommended_route_id: str
    recommendation_reason: str
    disclaimer: str

# Fishing Intelligence (PFZ)
class FishingZone(BaseModel):
    zone_id: str
    center: Dict[str, float]
    radius_km: float
    pfz_indicator_score: float # 0 - 100
    sst_gradient: float
    chlorophyll_concentration: float
    current_convergence: float
    confidence: float
    recommended_target_species: List[str]
    safety_advisory: str
    all_candidates: Optional[List[Dict[str, Any]]] = None

# Cyclone Monitoring
class CycloneTrackPoint(BaseModel):
    timestamp: str
    lat: float
    lon: float
    max_wind_knots: float
    pressure_hpa: float
    category: str # Tropical Depression, Cyclonic Storm, Severe Cyclonic Storm, Extremely Severe

class CycloneDetails(BaseModel):
    cyclone_id: str
    name: str
    status: str # ACTIVE, DISSIPATED, MONITORING
    current_location: Dict[str, float]
    movement_speed_kmh: float
    movement_direction: str
    max_sustained_wind_kmh: float
    central_pressure_hpa: float
    cone_of_uncertainty: List[Dict[str, float]]
    historical_track: List[CycloneTrackPoint]
    projected_track: List[CycloneTrackPoint]
    affected_ports: List[str]

# What-If Simulation
class WhatIfRequest(BaseModel):
    lat: float
    lon: float
    wind_increase_pct: float = 0.0
    wave_increase_pct: float = 0.0
    pressure_drop_hpa: float = 0.0
    cyclone_prob_increase: float = 0.0

class WhatIfResponse(BaseModel):
    original_risk: float
    simulated_risk: float
    risk_delta: float
    original_level: str
    simulated_level: str
    affected_route_impact: str
    top_contributing_changes: List[str]
    explanation: str

# Agent Observability & Trace
class AgentExecutionStep(BaseModel):
    agent_name: str
    status: str # PENDING, IN_PROGRESS, COMPLETED, FAILED, FALLBACK
    action_taken: str
    details: Dict[str, Any]
    timestamp: str

class AgentTraceResponse(BaseModel):
    query: str
    master_agent_plan: List[str]
    execution_steps: List[AgentExecutionStep]
    final_risk_assessment: Optional[RiskAssessmentResponse] = None
    final_answer: str
    detected_language: str = "en"
    detected_intents: List[str] = []
    selected_agents: List[str] = []
    evidence_sources: List[Dict[str, Any]] = []
    alerts: List[Dict[str, Any]] = []
    geofence_warnings: List[str] = []
    recommendations: List[str] = []
    structured_context: Optional[Dict[str, Any]] = None
    departure_optimization: Optional[Dict[str, Any]] = None
    geofence_summary: Optional[Dict[str, Any]] = None
    pfz_candidates: Optional[List[Dict[str, Any]]] = None
    safety_verification: Optional[Dict[str, Any]] = None


# RAG & Knowledge
class RAGQueryRequest(BaseModel):
    question: str
    top_k: int = 3

class RAGCitation(BaseModel):
    document_title: str
    category: str
    snippet: str
    relevance_score: float

class RAGQueryResponse(BaseModel):
    question: str
    answer: str
    citations: List[RAGCitation]

# Model Evaluation
class ModelMetricItem(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    model_name: str
    task: str # Risk Classification / Anomaly Detection
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    mae: float
    rmse: float

class EvaluationDashboardResponse(BaseModel):
    models: List[ModelMetricItem]
    confusion_matrix: Dict[str, Any]
    ground_truth_sample_count: int
    evaluation_note: str

# System Health & Data Source Status
class DataSourceHealth(BaseModel):
    name: str
    provider_type: str
    status: str # OPERATIONAL, DEGRADED, MOCK_FALLBACK
    latency_ms: int
    last_freshness: str
    trust_reliability: float

class SystemHealthResponse(BaseModel):
    status: str
    database: str
    operational_mode: str
    sources: List[DataSourceHealth]

# ─────────────────────────────────────────────────────────────────────────────
# NEW: Dedicated Location & Route Safety Intelligence Schemas
# ─────────────────────────────────────────────────────────────────────────────

class LocationAnalyseRequest(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude between -90 and 90")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude between -180 and 180")
    mode: str = Field(default="HYBRID", description="Operational mode: LIVE, HYBRID, or DEMO")

class SpecializedAgentSummary(BaseModel):
    agent: str
    status: str # SAFE, CAUTION, DANGER
    confidence: float
    summary: str
    reasons: List[str] = []
    recommendations: List[str] = []

class CollaborativeReasoningSummary(BaseModel):
    agreements: List[str] = []
    conflicts: List[str] = []
    consensus_level: str # SAFE, CAUTION, DANGER
    collaborative_summary: str

class LocationAnalyseResponse(BaseModel):
    latitude: float
    longitude: float
    location_name: str
    timestamp: str
    operational_mode: str
    risk_level: str # SAFE, CAUTION, DANGER
    risk_score: float # 0 - 100
    confidence: int # 0 - 100
    uncertainty_level: str
    current_conditions: Dict[str, Any]
    key_risks: List[str]
    risk_components: Dict[str, Any]
    agent_findings: List[SpecializedAgentSummary]
    collaborative_reasoning: CollaborativeReasoningSummary
    explainability: Dict[str, Any]
    recommendations: List[str]
    fused_record: CombinedMarineData

class AreaScanRequest(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    radius_km: float = Field(default=50.0, ge=5.0, le=300.0)
    mode: str = "HYBRID"

class DirectionalScanItem(BaseModel):
    direction: str
    label: str
    latitude: float
    longitude: float
    distance_km: float
    risk_level: str
    risk_score: float
    wave_height_m: float
    wind_speed_kmh: float
    key_risks: List[str]
    summary: str

class AreaScanResponse(BaseModel):
    center: Dict[str, float]
    radius_km: float
    current_location_safety: Dict[str, Any]
    directional_scans: List[DirectionalScanItem]
    predictive_threat_summary: List[str]
    recommended_heading: str

class RouteAnalyseRequest(BaseModel):
    origin_latitude: float = Field(..., ge=-90.0, le=90.0)
    origin_longitude: float = Field(..., ge=-180.0, le=180.0)
    destination_latitude: float = Field(..., ge=-90.0, le=90.0)
    destination_longitude: float = Field(..., ge=-180.0, le=180.0)
    origin_name: str = "Origin Port"
    destination_name: Optional[str] = "Destination Port"
    dest_name: Optional[str] = None
    mode: str = "HYBRID"

class RouteCheckpointItem(BaseModel):
    label: str
    distance_from_origin_km: float
    latitude: float
    longitude: float
    risk_level: str
    risk_score: float
    wave_height_m: float
    wind_speed_kmh: float
    key_risks: List[str]
    recommendation: str

class RouteAnalyseResponse(BaseModel):
    origin: Dict[str, Any]
    destination: Dict[str, Any]
    total_distance_km: float
    overall_route_safety: str # SAFE, CAUTION, DANGER
    max_risk_score: float
    progressive_checkpoints: List[RouteCheckpointItem]
    predictive_route_threats: List[str]
    route_clearance: str

class AgentStatusItem(BaseModel):
    agent_id: str
    name: str
    domain: str
    status: str
    confidence_weight: float
    capabilities: List[str]
