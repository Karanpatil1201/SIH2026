export interface LocationInfo {
  lat: number;
  lon: number;
  name?: string;
}

export interface DataQualityReport {
  quality_score: number;
  status: 'VALID' | 'WARNING' | 'INVALID';
  missing_fields: string[];
  anomalies: string[];
  freshness: string;
  issues: string[];
}

export interface CombinedMarineData {
  location: LocationInfo;
  timestamp: string;
  sst: number;
  wave_height: number;
  wave_direction: number;
  wave_period: number;
  swell_height: number;
  current_velocity: number;
  wind_speed: number;
  wind_direction: number;
  pressure: number;
  precipitation: number;
  salinity: number;
  chlorophyll: number;
  sea_level: number;
  quality_report: DataQualityReport;
  trust_score: number;
  data_source_mode: string;
  salinity_source?: string;
  chlorophyll_source?: string;
}

export interface FeatureContribution {
  feature: string;
  impact: number;
  value: any;
  description: string;
}

export interface RiskAssessmentResponse {
  location: LocationInfo;
  timestamp: string;
  risk_score: number;
  risk_level: 'SAFE' | 'CAUTION' | 'DANGER' | 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';
  confidence: number;
  uncertainty_level: string;
  top_positive_forces: FeatureContribution[];
  top_negative_forces: FeatureContribution[];
  fused_record: CombinedMarineData;
  recommended_action: string;
  disclaimer: string;
}

export interface AnomalyEvent {
  event_id: string;
  event_type: string;
  location: LocationInfo;
  severity: string;
  detected_at: string;
  confidence: number;
  evidence: string[];
}

export interface RoutePoint {
  lat: number;
  lon: number;
  risk_score: number;
  wave_height: number;
  wind_speed: number;
}

export interface RouteOption {
  route_id: string;
  name: string;
  waypoints: RoutePoint[];
  total_distance_km: number;
  estimated_time_hours: number;
  average_risk_score: number;
  max_wave_height: number;
  max_wind_speed: number;
  storm_exposure_pct: number;
  advisory_count: number;
  is_geofence_compliant?: boolean;
  is_rejected?: boolean;
  rejection_reason?: string;
  geofence_violations?: string[];
  geofence_warnings?: string[];
}

export interface RouteComparisonResponse {
  origin: LocationInfo;
  destination: LocationInfo;
  routes: RouteOption[];
  recommended_route_id: string;
  recommendation_reason: string;
  disclaimer: string;
}

export interface FishingZone {
  zone_id: string;
  center: { lat: number; lon: number };
  radius_km: number;
  pfz_indicator_score: number;
  sst_gradient: number;
  chlorophyll_concentration: number;
  current_convergence: number;
  confidence: number;
  recommended_target_species: string[];
  safety_advisory: string;
  disclaimer?: string;
  all_candidates?: any[];
}

export interface CycloneTrackPoint {
  timestamp: string;
  lat: number;
  lon: number;
  max_wind_knots: number;
  pressure_hpa: number;
  category: string;
}

export interface CycloneDetails {
  cyclone_id: string;
  name: string;
  status: string;
  current_location: { lat: number; lon: number };
  movement_speed_kmh: number;
  movement_direction: string;
  max_sustained_wind_kmh: number;
  central_pressure_hpa: number;
  cone_of_uncertainty: { lat: number; lon: number }[];
  historical_track: CycloneTrackPoint[];
  projected_track: CycloneTrackPoint[];
  affected_ports: string[];
}

export interface WhatIfRequest {
  lat: number;
  lon: number;
  wind_increase_pct: number;
  wave_increase_pct: number;
  pressure_drop_hpa: number;
  cyclone_prob_increase: number;
}

export interface WhatIfResponse {
  original_risk: number;
  simulated_risk: number;
  risk_delta: number;
  original_level: string;
  simulated_level: string;
  affected_route_impact: string;
  top_contributing_changes: string[];
  explanation: string;
}

export interface AgentExecutionStep {
  agent_name: string;
  status: string;
  action_taken: string;
  details: Record<string, any>;
  timestamp: string;
}

export interface AgentTraceResponse {
  query: string;
  master_agent_plan: string[];
  execution_steps: AgentExecutionStep[];
  final_risk_assessment?: RiskAssessmentResponse;
  final_answer: string;
  detected_language?: string;
  detected_intents?: string[];
  selected_agents?: string[];
  evidence_sources?: Array<{ name: string; agent: string; role: string; freshness?: string; trust?: number }>;
  alerts?: Array<{ severity: string; title: string; source: string }>;
  geofence_warnings?: string[];
  recommendations?: string[];
  structured_context?: any;
  departure_optimization?: any;
  geofence_summary?: any;
  pfz_candidates?: any[];
  safety_verification?: any;
}


export interface RAGCitation {
  document_title: string;
  category: string;
  snippet: string;
  relevance_score: number;
}

export interface RAGQueryResponse {
  question: string;
  answer: string;
  citations: RAGCitation[];
}

export interface ModelMetricItem {
  model_name: string;
  task: string;
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  roc_auc: number;
  mae: number;
  rmse: number;
}

export interface EvaluationDashboardResponse {
  models: ModelMetricItem[];
  confusion_matrix: Record<string, any>;
  ground_truth_sample_count: number;
  evaluation_note: string;
}

export interface DataSourceHealth {
  name: string;
  provider_type: string;
  status: string;
  latency_ms: number;
  last_freshness: string;
  trust_reliability: number;
}

export interface SystemHealthResponse {
  status: string;
  database: string;
  operational_mode: string;
  sources: DataSourceHealth[];
}

export interface ActiveAlert {
  id: number;
  title: string;
  message: string;
  severity: 'INFO' | 'WARNING' | 'CRITICAL';
  target_persona: string;
  location_name: string;
  latitude: number;
  longitude: number;
  timestamp: string;
}

export type PersonaType = 'Fisherman' | 'Shipping' | 'Disaster' | 'Researcher' | 'Admin';

export interface UserResponse {
  id: number;
  username: string;
  email: string;
  role: PersonaType;
  full_name?: string;
  is_active: boolean;
  created_at?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: UserResponse;
}

// ─────────────────────────────────────────────────────────────────────────────
// VARUNA Collaborative Agentic AI & Location Safety Types
// ─────────────────────────────────────────────────────────────────────────────

export interface SpecializedAgentSummary {
  agent: string;
  status: 'SAFE' | 'CAUTION' | 'DANGER' | string;
  confidence: number;
  summary: string;
  reasons: string[];
  recommendations: string[];
}

export interface CollaborativeReasoningSummary {
  agreements: string[];
  conflicts: string[];
  consensus_level: 'SAFE' | 'CAUTION' | 'DANGER' | string;
  collaborative_summary: string;
}

export interface LocationAnalyseResponse {
  latitude: number;
  longitude: number;
  location_name: string;
  timestamp: string;
  operational_mode: string;
  risk_level: 'SAFE' | 'CAUTION' | 'DANGER' | string;
  risk_score: number;
  confidence: number;
  uncertainty_level: string;
  current_conditions: {
    wave_height_m: number;
    wave_period_s?: number;
    swell_height_m?: number;
    current_velocity_ms?: number;
    wind_speed_kmh: number;
    wind_direction_deg?: number;
    surface_pressure_hpa?: number;
    sea_surface_temp_c?: number;
    precipitation_mm?: number;
    salinity_psu?: number;
    chlorophyll_mg_m3?: number;
    data_freshness?: string;
    data_quality_score?: number;
    trust_score?: number;
  };
  key_risks: string[];
  risk_components?: {
    ocean_risk: number;
    weather_risk: number;
    anomaly_risk: number;
    ml_prediction_risk: number;
    agent_confidence: number;
  };
  agent_findings: SpecializedAgentSummary[];
  collaborative_reasoning: CollaborativeReasoningSummary;
  explainability: {
    top_positive_forces: FeatureContribution[];
    top_negative_forces: FeatureContribution[];
  };
  recommendations: string[];
  fused_record: CombinedMarineData;
}

export interface DirectionalScanItem {
  direction: string;
  label: string;
  latitude: number;
  longitude: number;
  distance_km: number;
  risk_level: 'SAFE' | 'CAUTION' | 'DANGER' | string;
  risk_score: number;
  wave_height_m: number;
  wind_speed_kmh: number;
  key_risks: string[];
  summary: string;
}

export interface AreaScanResponse {
  center: { latitude: number; longitude: number };
  radius_km: number;
  current_location_safety: {
    risk_level: string;
    risk_score: number;
    confidence: number;
    summary: string;
  };
  directional_scans: DirectionalScanItem[];
  predictive_threat_summary: string[];
  recommended_heading: string;
}

export interface RouteCheckpointItem {
  label: string;
  distance_from_origin_km: number;
  latitude: number;
  longitude: number;
  risk_level: 'SAFE' | 'CAUTION' | 'DANGER' | string;
  risk_score: number;
  wave_height_m: number;
  wind_speed_kmh: number;
  key_risks: string[];
  recommendation: string;
}

export interface RouteAnalyseResponse {
  origin: { name: string; latitude: number; longitude: number };
  destination: { name: string; latitude: number; longitude: number };
  total_distance_km: number;
  overall_route_safety: 'SAFE' | 'CAUTION' | 'DANGER' | string;
  max_risk_score: number;
  progressive_checkpoints: RouteCheckpointItem[];
  predictive_route_threats: string[];
  route_clearance: string;
}

export interface AgentStatusItem {
  agent_id: string;
  name: string;
  domain: string;
  status: string;
  confidence_weight: number;
  capabilities: string[];
}
