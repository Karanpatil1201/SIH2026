import os
import hashlib
import secrets
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session

from app.core.database import get_db, engine, Base
from app.core.config import settings
from app.core.security import get_password_hash, verify_password, create_access_token, decode_access_token
from app.models.database_models import (
    UserDB, AlertDB, AdvisoryDB, RiskAssessmentDB, SimulationRunDB, FeedbackDB, 
    OTPChallengeDB, UserSessionDB, QueryHistoryDB, ActivityLogDB
)
from app.models.schemas import (
    UserCreate, UserResponse, LoginRequest, Token, OTPRequest, OTPVerifyRequest,
    RiskAssessmentResponse, RouteComparisonResponse, AnomalyEvent,
    FishingZone, CycloneDetails, CycloneTrackPoint, WhatIfRequest, WhatIfResponse,
    AgentTraceResponse, RAGQueryRequest, RAGQueryResponse,
    EvaluationDashboardResponse, SystemHealthResponse, DataSourceHealth,
    LocationAnalyseRequest, LocationAnalyseResponse,
    AreaScanRequest, AreaScanResponse,
    RouteAnalyseRequest, RouteAnalyseResponse,
    AgentStatusItem,
    MarineWhyEngine, DecisionDNA, AgentDissentResponse, MarineTimelineResponse,
    MarineMissionProfileRequest, MarineMissionProfileResponse,
    WhatIfEnhancedRequest, WhatIfEnhancedResponse
)

from app.agents.collaborative_engine import CollaborativeAIEngine
from app.agents.master_agent import MasterAgent
from app.fusion.fusion_engine import DataFusionEngine
from app.providers.openmeteo import OpenMeteoMarineProvider, OpenMeteoWeatherProvider
from app.providers.copernicus import CopernicusMarineService
from app.providers.satellite import SatelliteDataService
from app.providers.advisory import AdvisoryService
from app.providers.demo import DemoOceanProvider
from app.gis.pathfinding import RoutePathfinder
from app.ml.xgboost_risk import XGBoostRiskModel
from app.ml.isolation_forest import AnomalyDetector
from app.ml.shap_explainer import ShapExplainer
from app.ml.evaluator import GroundTruthEvaluator
from app.rag.rag_engine import MarineKnowledgeRAG
from app.simulation.simulator import WhatIfSimulationEngine
from app.reports.pdf_generator import MarineReportGenerator
from app.providers.ecosystem_dataset import EcosystemClimateDataset
from app.providers.fisheries_dataset import get_summary as get_fisheries_dataset_summary
from app.gis.spatial_data import (
    IMBL_BOUNDARIES, RESTRICTED_ZONES, MARINE_PROTECTED_AREAS,
    ECOLOGICALLY_SENSITIVE_ZONES, COASTAL_PORTS_AND_HARBOURS
)
from app.tools.registry import tool_registry
from app.agents.language_service import LanguageService

from app.models.database_models import NotificationDB
from app.services.notification.dispatcher import notification_dispatcher
from app.services.notification.schemas import (
    NotificationSendRequest, NotificationBulkRequest, NotificationTestRequest,
    RiskAlertTriggerRequest, DeviceRegistrationRequest, NotificationPreferenceUpdate,
    NotificationResponse, NotificationBulkResponse, NotificationHistoryItem,
    NotificationHistoryResponse, NotificationChannelsStatusResponse, ChannelHealthItem,
)

# Ensure DB tables exist
Base.metadata.create_all(bind=engine)

router = APIRouter()

# Instantiate Core Singletons
master_agent = MasterAgent()
route_pathfinder = RoutePathfinder()
xgb_risk_model = XGBoostRiskModel()
anomaly_detector = AnomalyDetector()
shap_explainer = ShapExplainer(xgb_risk_model)
simulation_engine = WhatIfSimulationEngine()


def _send_login_notification(
    email: str,
    username: str,
    db: Session,
    user_id: Optional[int] = None,
) -> None:
    """Record and deliver a login security notification to the account email."""
    notification_dispatcher.send(
        channel="EMAIL",
        recipient=email,
        subject="VARUNA login notification",
        body=(
            f"A successful login was recorded for the VARUNA account '{username}'.\n\n"
            f"Time: {datetime.now(timezone.utc).isoformat()}\n"
            "If this was not you, change your password immediately."
        ),
        severity="INFO",
        db=db,
        user_id=user_id,
        notification_type="GENERAL",
    )


# --- Auth Routes ---
@router.post("/auth/request-otp")
def request_login_otp(req: OTPRequest, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.email == req.email.strip().lower(), UserDB.is_active == True).first()
    if not user:
        raise HTTPException(status_code=404, detail="No active account is registered with this email address")

    otp = f"{secrets.randbelow(1_000_000):06d}"
    challenge = OTPChallengeDB(
        email=user.email.lower(),
        code_hash=hashlib.sha256(otp.encode("utf-8")).hexdigest(),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )
    db.add(challenge)
    db.commit()

    result = notification_dispatcher.send(
        channel="EMAIL",
        recipient=user.email,
        subject="Your VARUNA login OTP",
        body=(
            f"Your VARUNA login verification code is: {otp}\n\n"
            "This code expires in 10 minutes and can be used only once."
        ),
        severity="INFO",
        db=db,
        user_id=user.id,
        notification_type="TEST",
    )
    if result["status"] == "FAILED":
        raise HTTPException(status_code=503, detail="Unable to send the OTP email. Please try again.")
    return {"message": "OTP sent to your registered email address", "demo_mode": result.get("demo_mode", False)}


@router.post("/auth/verify-otp", response_model=Token)
def verify_login_otp(req: OTPVerifyRequest, db: Session = Depends(get_db)):
    email = req.email.strip().lower()
    challenge = (
        db.query(OTPChallengeDB)
        .filter(
            OTPChallengeDB.email == email,
            OTPChallengeDB.consumed_at.is_(None),
        )
        .order_by(OTPChallengeDB.created_at.desc())
        .first()
    )
    now = datetime.now(timezone.utc)
    if not challenge or challenge.expires_at.replace(tzinfo=timezone.utc) < now:
        raise HTTPException(status_code=400, detail="OTP is invalid or expired")
    if not secrets.compare_digest(
        challenge.code_hash,
        hashlib.sha256(req.otp.encode("utf-8")).hexdigest(),
    ):
        raise HTTPException(status_code=400, detail="OTP is invalid or expired")

    user = db.query(UserDB).filter(UserDB.email == email, UserDB.is_active == True).first()
    if not user:
        raise HTTPException(status_code=404, detail="User account is no longer active")
    
    challenge.consumed_at = now
    
    # Update last login
    user.last_login = now
    
    # Create user session
    session = UserSessionDB(user_id=user.id, login_time=now)
    db.add(session)
    
    # Create activity log
    activity = ActivityLogDB(user_id=user.id, action="LOGIN_OTP")
    db.add(activity)
    
    db.commit()
    token = create_access_token({"sub": user.username, "role": user.role})
    return Token(access_token=token, token_type="bearer", user=user)


@router.post("/auth/register", response_model=UserResponse)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(UserDB).filter(UserDB.username == user_in.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    if db.query(UserDB).filter(UserDB.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = UserDB(
        username=user_in.username,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role,
        full_name=user_in.full_name,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/auth/login", response_model=Token)
def login_user(req: LoginRequest, db: Session = Depends(get_db)):
    if "@" in req.username:
        email = req.username
        user = db.query(UserDB).filter(UserDB.email == email).first()
    else:
        user = db.query(UserDB).filter(UserDB.username == req.username).first()
        if user:
            email = user.email
        else:
            email = None
            
    if not user or not verify_password(req.password, user.hashed_password):
        # Demo accounts stay usable in a newly initialized local database.
        if req.username.lower() in ["fisherman", "shipping", "disaster", "researcher", "admin"] and req.password == "demo123":
            role = req.username.capitalize()
            user_resp = UserResponse(
                id=0, username=req.username, email=f"{req.username}@varuna.gov.in",
                role=role, full_name=f"SIH Demo {role}",
                is_active=True, created_at=datetime.now(timezone.utc),
            )
            token = create_access_token({"sub": req.username, "role": role})
            return Token(access_token=token, token_type="bearer", user=user_resp)
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    now = datetime.now(timezone.utc)
    user.last_login = now
    db.add(UserSessionDB(user_id=user.id, login_time=now))
    db.add(ActivityLogDB(user_id=user.id, action="LOGIN_PASSWORD"))
    db.commit()
    token = create_access_token({"sub": user.username, "role": user.role})
    if user.notification_email:
        _send_login_notification(user.email, user.username, db, user.id)
    return Token(access_token=token, token_type="bearer", user=user)

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> UserDB:
    payload = decode_access_token(credentials.credentials)
    username = payload.get("sub") if payload else None
    user = db.query(UserDB).filter(UserDB.username == username).first() if username else None
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user

from fastapi.security.utils import get_authorization_scheme_param
from fastapi import Request

def get_current_user_optional(request: Request, db: Session = Depends(get_db)) -> Optional[UserDB]:
    authorization = request.headers.get("Authorization")
    if not authorization:
        return None
    scheme, token = get_authorization_scheme_param(authorization)
    if scheme.lower() != "bearer":
        return None
    
    payload = decode_access_token(token)
    username = payload.get("sub") if payload else None
    return db.query(UserDB).filter(UserDB.username == username).first() if username else None

@router.post("/auth/logout")
def logout(current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    
    # Find active session and update logout_time
    session = db.query(UserSessionDB).filter(
        UserSessionDB.user_id == current_user.id,
        UserSessionDB.logout_time.is_(None)
    ).order_by(UserSessionDB.login_time.desc()).first()
    
    if session:
        session.logout_time = now
        
    activity = ActivityLogDB(user_id=current_user.id, action="LOGOUT")
    db.add(activity)
    db.commit()
    
    return {"message": "Logged out successfully"}


@router.get("/auth/otp-demo-peek")
def otp_demo_peek(email: str, db: Session = Depends(get_db)):
    """
    SIH Demo Mode: Returns the most recent un-consumed OTP for an email address.
    This endpoint is for demo/hackathon use only — disable before production deployment.
    It allows evaluators to complete OTP login without a working SMTP server.
    """
    email = email.strip().lower()
    challenge = (
        db.query(OTPChallengeDB)
        .filter(
            OTPChallengeDB.email == email,
            OTPChallengeDB.consumed_at.is_(None),
        )
        .order_by(OTPChallengeDB.created_at.desc())
        .first()
    )
    now = datetime.now(timezone.utc)
    if not challenge or challenge.expires_at.replace(tzinfo=timezone.utc) < now:
        raise HTTPException(
            status_code=404,
            detail="No active OTP found. Please request a new OTP first."
        )
    # Reverse-lookup the code from a known set — we can only show it exists; the actual
    # plaintext code is not stored. Instead, we brute-force the 6-digit space (fast, 1M ops max).
    # This is acceptable only in a controlled demo environment.
    for code_int in range(1_000_000):
        candidate = f"{code_int:06d}"
        if hashlib.sha256(candidate.encode()).hexdigest() == challenge.code_hash:
            expires_in_s = int((challenge.expires_at.replace(tzinfo=timezone.utc) - now).total_seconds())
            return {
                "demo_otp": candidate,
                "email": email,
                "expires_in_seconds": expires_in_s,
                "note": "DEMO MODE ONLY — disable /auth/otp-demo-peek before production deployment"
            }
    raise HTTPException(status_code=500, detail="Could not recover OTP (hash mismatch).")


@router.get("/auth/me")
def get_current_user_profile(token: str, db: Session = Depends(get_db)):
    """Validate a JWT access token and return the associated user profile."""
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    username = payload["sub"]
    user = db.query(UserDB).filter(UserDB.username == username, UserDB.is_active == True).first()
    if not user:
        # Demo user fallback
        from app.models.schemas import UserResponse as UserResp
        return UserResp(
            id=0, username=username,
            email=f"{username}@varuna.gov.in",
            role=payload.get("role", "Fisherman"),
            full_name=f"Demo {username.capitalize()}",
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
    return user



# ─────────────────────────────────────────────────────────────────────────────
# 1. CORE LOCATION SAFETY INTELLIGENCE (LIVE GPS & MANUAL INPUT)
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/location/analyse", response_model=LocationAnalyseResponse)
def analyse_location(req: LocationAnalyseRequest):
    """
    Primary endpoint for Live GPS or Manual Coordinate Marine Safety Analysis.
    Fetches live marine data, executes collaborative multi-agent reasoning,
    evaluates risk engine components, and returns structured SAFE / CAUTION / DANGER findings.
    """
    try:
        return master_agent.analyse_location(lat=req.latitude, lon=req.longitude, mode=req.mode)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Location analysis failed: {str(e)}")

@router.get("/location/live-analysis", response_model=LocationAnalyseResponse)
def get_live_location_analysis(
    lat: float = Query(..., ge=-90.0, le=90.0, description="Latitude"),
    lon: float = Query(..., ge=-180.0, le=180.0, description="Longitude"),
    mode: str = Query("LIVE", description="Operational mode: LIVE, HYBRID, DEMO")
):
    """
    GET convenience endpoint for real-time marine safety at specific coordinates.
    """
    try:
        return master_agent.analyse_location(lat=lat, lon=lon, mode=mode)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Live location analysis failed: {str(e)}")

# ─────────────────────────────────────────────────────────────────────────────
# 2. PREDICTIVE LOCATION & AREA SCANNING
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/location/area-scan", response_model=AreaScanResponse)
def scan_surrounding_area(req: AreaScanRequest):
    """
    Mode 1: Predictive Location Area Scan.
    Evaluates current position and 8 directional sectors (N, NE, E, SE, S, SW, W, NW)
    at specified radius (e.g. 50km) to predict incoming or nearby marine hazards.
    """
    try:
        return master_agent.scan_area(lat=req.latitude, lon=req.longitude, radius_km=req.radius_km, mode=req.mode)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Area scan failed: {str(e)}")

# ─────────────────────────────────────────────────────────────────────────────
# 3. PREDICTIVE ROUTE SAFETY INTELLIGENCE
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/route/analyse", response_model=RouteAnalyseResponse)
def analyse_route_safety(req: RouteAnalyseRequest):
    """
    Mode 2: Predictive Route Safety Intelligence.
    Evaluates progressive intervals along the transit route (Current, 10km ahead, 25km ahead, 50km ahead, Destination).
    """
    try:
        return master_agent.analyse_route(
            origin_lat=req.origin_latitude,
            origin_lon=req.origin_longitude,
            dest_lat=req.destination_latitude,
            dest_lon=req.destination_longitude,
            origin_name=req.origin_name,
            dest_name=getattr(req, "destination_name", getattr(req, "dest_name", "Destination Port")),
            mode=req.mode
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Route analysis failed: {str(e)}")

# ─────────────────────────────────────────────────────────────────────────────
# 4. COLLABORATIVE AGENT STATUS & OBSERVABILITY
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/agents/status", response_model=List[AgentStatusItem])
def get_agents_status():
    """
    Returns registry, capabilities, and operational health of all specialized agents.
    """
    return master_agent.get_all_agents_status()

# ─────────────────────────────────────────────────────────────────────────────
# 5. DOMAIN-SPECIFIC MARINE INTELLIGENCE ENDPOINTS (PRESERVED FOR FRONTEND)
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/ocean")
def get_ocean_data(lat: float = 18.9667, lon: float = 72.8333, mode: str = "LIVE"):
    return master_agent.ocean_agent.process(lat, lon, mode=mode)

@router.get("/weather")
def get_weather_data(lat: float = 18.9667, lon: float = 72.8333, mode: str = "LIVE"):
    return master_agent.weather_agent.process(lat, lon, mode=mode)

@router.get("/satellite")
def get_satellite_data(lat: float = 18.9667, lon: float = 72.8333):
    return master_agent.satellite_agent.process(lat, lon)

@router.get("/gis")
def get_gis_info(lat: float = 18.9667, lon: float = 72.8333):
    return master_agent.gis_agent.process(lat, lon)

@router.get("/risk", response_model=RiskAssessmentResponse)
def get_risk_assessment(lat: float = 18.9667, lon: float = 72.8333, mode: str = "LIVE"):
    loc_analysis = master_agent.analyse_location(lat, lon, mode=mode)
    fused_record = loc_analysis["fused_record"]

    return RiskAssessmentResponse(
        location={"lat": lat, "lon": lon, "name": loc_analysis["location_name"]},
        timestamp=fused_record.timestamp,
        risk_score=loc_analysis["risk_score"],
        risk_level=loc_analysis["risk_level"],
        confidence=loc_analysis["confidence"] / 100.0,
        uncertainty_level=loc_analysis["uncertainty_level"],
        top_positive_forces=loc_analysis["explainability"]["top_positive_forces"],
        top_negative_forces=loc_analysis["explainability"]["top_negative_forces"],
        fused_record=fused_record,
        recommended_action=loc_analysis["recommendations"][0] if loc_analysis["recommendations"] else "Safe baseline marine state.",
        disclaimer="Marine risk score calculated via VARUNA Collaborative Agentic AI & XGBoost ML."
    )

@router.get("/anomaly")
def get_anomaly_detection(lat: float = 18.9667, lon: float = 72.8333):
    demo = DemoOceanProvider.get_demo_record(lat, lon)
    return master_agent.anomaly_agent.process(demo)

@router.get("/routes", response_model=RouteComparisonResponse)
def get_route_comparison(
    origin_lat: float = 18.9667, origin_lon: float = 72.8333,
    dest_lat: float = 15.4989, dest_lon: float = 73.8278,
    origin_name: str = "Mumbai Port", dest_name: str = "Goa Port"
):
    return route_pathfinder.find_routes(origin_lat, origin_lon, dest_lat, dest_lon, origin_name, dest_name)

@router.get("/fishing")
def get_fishing_intelligence(lat: float = 18.9667, lon: float = 72.8333, mode: str = "LIVE"):
    ocean_res = master_agent.ocean_agent.process(lat, lon, mode=mode)
    fish_res = master_agent.fisheries_agent.process(lat, lon, ocean_res["findings"])
    findings = fish_res.get("findings", {})
    top_pfz = findings.get("primary_pfz", {})
    return {
        "zone_id": findings.get("zone_id", "PFZ-IND-01"),
        "center": top_pfz.get("center", {"lat": lat, "lon": lon}),
        "radius_km": 15.0,
        "pfz_indicator_score": top_pfz.get("fishing_potential_score", 82.5),
        "sst_gradient": 0.42,
        "chlorophyll_concentration": top_pfz.get("chlorophyll_mg_m3", 1.25),
        "current_convergence": 0.35,
        "confidence": fish_res.get("confidence", 0.91),
        "recommended_target_species": findings.get("target_species", ["Indian Mackerel", "Oil Sardine"]),
        "safety_advisory": fish_res["recommendations"][0] if fish_res.get("recommendations") else "PFZ verified.",
        "disclaimer": "Potential fishing zone indicator based on ocean colour & SST fronts, not guaranteed fish location."
    }

@router.get("/cyclone", response_model=CycloneDetails)
def get_cyclone_monitoring():
    now = datetime.now(timezone.utc)
    return CycloneDetails(
        cyclone_id="CYCLONE-2026-03B",
        name="Cyclonic Storm 'ASNA'",
        status="ACTIVE",
        current_location={"lat": 16.5, "lon": 86.2},
        movement_speed_kmh=18.5,
        movement_direction="NW",
        max_sustained_wind_kmh=95.0,
        central_pressure_hpa=988.0,
        cone_of_uncertainty=[
            {"lat": 16.5, "lon": 86.2},
            {"lat": 17.8, "lon": 85.0},
            {"lat": 19.2, "lon": 84.1}
        ],
        historical_track=[
            CycloneTrackPoint(timestamp=(now - timedelta(hours=24)).isoformat(), lat=14.2, lon=88.5, max_wind_knots=40, pressure_hpa=1002, category="Deep Depression"),
            CycloneTrackPoint(timestamp=(now - timedelta(hours=12)).isoformat(), lat=15.3, lon=87.2, max_wind_knots=52, pressure_hpa=994, category="Cyclonic Storm")
        ],
        projected_track=[
            CycloneTrackPoint(timestamp=(now + timedelta(hours=12)).isoformat(), lat=17.8, lon=85.0, max_wind_knots=60, pressure_hpa=982, category="Severe Cyclonic Storm"),
            CycloneTrackPoint(timestamp=(now + timedelta(hours=24)).isoformat(), lat=19.2, lon=84.1, max_wind_knots=65, pressure_hpa=978, category="Severe Cyclonic Storm")
        ],
        affected_ports=["Visakhapatnam Port", "Paradip Port", "Dhamra Port"]
    )

@router.get("/advisories")
def get_marine_advisories(region: str = "Arabian Sea"):
    return master_agent.advisory_agent.process(region)

@router.get("/alerts")
def get_active_alerts(persona: str = "ALL"):
    return [
        {
            "id": 1,
            "title": "High Wave & Strong Wind Warning",
            "message": "Wave heights exceeding 2.8 meters detected offshore Mumbai. Small fishing craft restricted.",
            "severity": "CRITICAL",
            "target_persona": "Fisherman",
            "location_name": "Mumbai Offshore",
            "latitude": 18.9667,
            "longitude": 72.8333,
            "timestamp": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": 2,
            "title": "Coastal Current Shear Advisory",
            "message": "Current velocity shear of 0.6 m/s along Mumbai-Goa shipping corridor. Adjust route heading.",
            "severity": "WARNING",
            "target_persona": "Shipping",
            "location_name": "Goa Corridor",
            "latitude": 16.2,
            "longitude": 73.2,
            "timestamp": (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat()
        }
    ]

@router.get("/history")
def get_historical_trends(hours: int = 24, lat: float = 18.9667, lon: float = 72.8333):
    now = datetime.now(timezone.utc)
    series = []
    for h in range(hours, 0, -2):
        ts = (now - timedelta(hours=h)).isoformat()
        w_h = round(1.4 + 0.6 * float((h % 6) / 6.0), 2)
        w_s = round(16.0 + 10.0 * float((h % 8) / 8.0), 1)
        r_s = round((w_h / 3.0) * 40.0 + (w_s / 35.0) * 40.0, 1)
        series.append({
            "timestamp": ts,
            "sst": round(28.4 + 0.2 * (h % 3), 2),
            "wave_height": w_h,
            "wind_speed": w_s,
            "pressure": round(1012.0 - 2.0 * (h % 4), 1),
            "risk_score": r_s
        })
    return {"location": {"lat": lat, "lon": lon}, "history": series}

@router.post("/simulation", response_model=WhatIfResponse)
def run_whatif_simulation(req: WhatIfRequest):
    return simulation_engine.run_simulation(req)

@router.post("/marine/why", response_model=MarineWhyEngine)
def get_marine_why(payload: Dict[str, Any]):
    lat = float(payload.get("lat", payload.get("latitude", 18.9667)))
    lon = float(payload.get("lon", payload.get("longitude", 72.8333)))
    mode = payload.get("mode", "HYBRID")
    analysis = master_agent.analyse_location(lat, lon, mode)
    return analysis["why_engine"]

@router.post("/marine/decision-dna", response_model=DecisionDNA)
def get_marine_decision_dna(payload: Dict[str, Any]):
    lat = float(payload.get("lat", payload.get("latitude", 18.9667)))
    lon = float(payload.get("lon", payload.get("longitude", 72.8333)))
    mode = payload.get("mode", "HYBRID")
    analysis = master_agent.analyse_location(lat, lon, mode)
    return analysis["decision_dna"]

@router.post("/marine/agent-dissent", response_model=AgentDissentResponse)
def get_agent_dissent(payload: Dict[str, Any]):
    lat = float(payload.get("lat", payload.get("latitude", 18.9667)))
    lon = float(payload.get("lon", payload.get("longitude", 72.8333)))
    mode = payload.get("mode", "HYBRID")
    analysis = master_agent.analyse_location(lat, lon, mode)
    return analysis["agent_dissent"]

@router.post("/marine/timeline", response_model=MarineTimelineResponse)
def get_marine_timeline(payload: Dict[str, Any]):
    lat = float(payload.get("lat", payload.get("latitude", 18.9667)))
    lon = float(payload.get("lon", payload.get("longitude", 72.8333)))
    mode = payload.get("mode", "HYBRID")
    analysis = master_agent.analyse_location(lat, lon, mode)
    return analysis["timeline"]

@router.post("/mission/analyze", response_model=MarineMissionProfileResponse)
def analyze_mission_profile(req: MarineMissionProfileRequest):
    analysis = master_agent.analyse_location(req.latitude, req.longitude, req.mode)
    return CollaborativeAIEngine.evaluate_mission_profile(
        req=req,
        current_conditions=analysis["current_conditions"],
        agent_findings=analysis["agent_findings"],
        base_risk_score=analysis["risk_score"],
        location_name=analysis["location_name"]
    )

@router.post("/scenario/simulate-enhanced", response_model=WhatIfEnhancedResponse)
def run_whatif_enhanced(req: WhatIfEnhancedRequest):
    analysis = master_agent.analyse_location(req.lat, req.lon, "HYBRID")
    return CollaborativeAIEngine.evaluate_what_if_enhanced(
        req=req,
        current_conditions=analysis["current_conditions"],
        base_risk_score=analysis["risk_score"]
    )

@router.post("/chat", response_model=AgentTraceResponse)
def chat_with_agent(payload: Dict[str, Any], current_user: Optional[UserDB] = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    query = payload.get("query", "What is the marine risk near Mumbai tomorrow?")
    lat = float(payload.get("lat", 18.9667))
    lon = float(payload.get("lon", 72.8333))
    mode = payload.get("mode", "HYBRID")
    conversation_history = payload.get("conversation_history", [])
    session_id = payload.get("session_id", "varuna_session")
    
    response = master_agent.process_query(
        query,
        lat=lat,
        lon=lon,
        mode=mode,
        conversation_history=conversation_history,
        session_id=session_id
    )
    
    if current_user:
        lang = getattr(response, "detected_language", "en") if hasattr(response, "detected_language") else (response.get("detected_language", "en") if isinstance(response, dict) else "en")
        history = QueryHistoryDB(
            user_id=current_user.id,
            query=query,
            language=lang,
            latitude=lat,
            longitude=lon,
            response_status="SUCCESS"
        )
        db.add(history)
        
        activity = ActivityLogDB(user_id=current_user.id, action="QUERY_CHAT")
        db.add(activity)
        db.commit()
        
    return response

@router.get("/geofence/layers")
def get_geofence_layers():
    """
    Returns all GIS layers (IMBL lines, Restricted Polygons, MPAs, ESZs, and Ports)
    for rendering on the frontend marine map.
    """
    return {
        "imbl_boundaries": IMBL_BOUNDARIES,
        "restricted_zones": RESTRICTED_ZONES,
        "marine_protected_areas": MARINE_PROTECTED_AREAS,
        "ecologically_sensitive_zones": ECOLOGICALLY_SENSITIVE_ZONES,
        "coastal_ports": COASTAL_PORTS_AND_HARBOURS
    }

@router.get("/geofence/check")
def check_point_geofence(lat: float = 18.9667, lon: float = 72.8333):
    """
    Evaluates point coordinates against all spatial geofence layers.
    """
    return master_agent.geofencing_agent.process(lat, lon)

@router.get("/departure/optimize")
def get_departure_optimization(lat: float = 18.9667, lon: float = 72.8333, base_time: Optional[str] = None):
    """
    Calculates departure time risk curve across multiple time windows (06:00 to 14:00).
    """
    return route_pathfinder.optimize_departure_windows(lat, lon, base_time)

@router.get("/tools")
def get_registered_tools():
    """
    Returns all registered tools available to the autonomous Master Orchestrator.
    """
    return tool_registry.list_tools()

@router.get("/languages")
def get_supported_languages():
    """
    Returns list of supported Indian languages for automatic identification and localized output.
    """
    return LanguageService.SUPPORTED_LANGUAGES

@router.post("/rag", response_model=RAGQueryResponse)
def query_rag(req: RAGQueryRequest, current_user: Optional[UserDB] = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    response = MarineKnowledgeRAG.query_knowledge(req.question, top_k=req.top_k)
    
    if current_user:
        history = QueryHistoryDB(
            user_id=current_user.id,
            query=req.question,
            language="en",
            response_status="SUCCESS"
        )
        db.add(history)
        
        activity = ActivityLogDB(user_id=current_user.id, action="QUERY_RAG")
        db.add(activity)
        db.commit()
        
    return response

@router.post("/reports")
def generate_report(payload: Dict[str, Any]):
    output_filename = f"varuna_report_{int(datetime.now(timezone.utc).timestamp())}.pdf"
    out_path = os.path.join(os.path.dirname(__file__), "..", "..", "static", "reports", output_filename)
    norm_path = os.path.abspath(out_path)
    
    MarineReportGenerator.generate_pdf_report(payload, norm_path)
    return {"report_url": f"/static/reports/{output_filename}", "filename": output_filename}

@router.get("/static/reports/{filename}")
def download_report(filename: str):
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "static", "reports", filename))
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/pdf", filename=filename)
    raise HTTPException(status_code=404, detail="Report file not found")

@router.get("/data-sources")
def get_data_sources():
    copernicus_status = "OPERATIONAL" if settings.COPERNICUS_USERNAME and settings.COPERNICUS_PASSWORD else "MOCK_FALLBACK"
    copernicus_freshness = "LIVE" if copernicus_status == "OPERATIONAL" else "DEMO"
    return [
        {"name": "Open-Meteo Marine API", "provider_type": "Real-time Wave & Current Forecast", "status": "OPERATIONAL", "latency_ms": 75, "last_freshness": "LIVE", "trust_reliability": 0.94},
        {"name": "Open-Meteo Weather API", "provider_type": "Real-time Meteorological Forecast", "status": "OPERATIONAL", "latency_ms": 70, "last_freshness": "LIVE", "trust_reliability": 0.94},
        {"name": "Copernicus Marine Service", "provider_type": "Live salinity, SST and chlorophyll enrichment", "status": copernicus_status, "latency_ms": 0 if copernicus_status == "MOCK_FALLBACK" else 1800, "last_freshness": copernicus_freshness, "trust_reliability": 0.94 if copernicus_status == "OPERATIONAL" else 0.70},
        {"name": "Sentinel-3 OLCI / MODIS Aqua", "provider_type": "Remote Sensing Ocean Colour & Turbidity", "status": copernicus_status, "latency_ms": 0 if copernicus_status == "MOCK_FALLBACK" else 1800, "last_freshness": copernicus_freshness, "trust_reliability": 0.88 if copernicus_status == "OPERATIONAL" else 0.70},
        {"name": "INCOIS / IMD Advisories", "provider_type": "Government Maritime Safety Bulletins", "status": "MOCK_FALLBACK", "latency_ms": 0, "last_freshness": "DEMO", "trust_reliability": 0.70},
        {"name": "Historical Ecosystem Climate Dataset", "provider_type": "2015 SST, pH, bleaching, species and heatwave observations", "status": EcosystemClimateDataset.summary()["status"], "latency_ms": 0, "last_freshness": "HISTORICAL", "trust_reliability": 0.80}
        ,{"name": "FAO Fisheries Catch Dataset", "provider_type": "Historical catch quantities by country, species, period and water area", "status": get_fisheries_dataset_summary()["status"], "latency_ms": 0, "last_freshness": "HISTORICAL", "trust_reliability": 0.82}
    ]

@router.get("/model-status", response_model=EvaluationDashboardResponse)
def get_model_status():
    return GroundTruthEvaluator.evaluate_all_models()

@router.get("/health", response_model=SystemHealthResponse)
def get_system_health():
    copernicus_status = "OPERATIONAL" if settings.COPERNICUS_USERNAME and settings.COPERNICUS_PASSWORD else "MOCK_FALLBACK"
    copernicus_freshness = "LIVE" if copernicus_status == "OPERATIONAL" else "DEMO"
    return SystemHealthResponse(
        status="HEALTHY" if copernicus_status == "OPERATIONAL" else "DEGRADED",
        database="CONNECTED (SQLite / PostgreSQL Ready)",
        operational_mode="HYBRID (Open-Meteo + Copernicus live; advisory fallback; historical datasets)",
        sources=[
            DataSourceHealth(name="Open-Meteo Marine", provider_type="Wave & Currents", status="OPERATIONAL", latency_ms=75, last_freshness="LIVE", trust_reliability=0.94),
            DataSourceHealth(name="Open-Meteo Weather", provider_type="Wind & Pressure", status="OPERATIONAL", latency_ms=70, last_freshness="LIVE", trust_reliability=0.94),
            DataSourceHealth(name="Copernicus Marine", provider_type="Live salinity / SST / chlorophyll", status=copernicus_status, latency_ms=0 if copernicus_status == "MOCK_FALLBACK" else 1800, last_freshness=copernicus_freshness, trust_reliability=0.94 if copernicus_status == "OPERATIONAL" else 0.70),
            DataSourceHealth(name="Sentinel-3 / MODIS", provider_type="Remote sensing proxy via Copernicus BGC", status=copernicus_status, latency_ms=0 if copernicus_status == "MOCK_FALLBACK" else 1800, last_freshness=copernicus_freshness, trust_reliability=0.88 if copernicus_status == "OPERATIONAL" else 0.70),
            DataSourceHealth(name="Ecosystem Climate Dataset", provider_type="Historical SST / pH / bleaching observations", status=EcosystemClimateDataset.summary()["status"], latency_ms=0, last_freshness="HISTORICAL", trust_reliability=0.80)
            ,DataSourceHealth(name="FAO Fisheries Catch Dataset", provider_type="Historical catch quantities", status=get_fisheries_dataset_summary()["status"], latency_ms=0, last_freshness="HISTORICAL", trust_reliability=0.82)
        ]
    )

@router.get("/fisheries/dataset")
def get_fisheries_dataset_status():
    """Return metadata for the integrated historical fisheries catch dataset."""
    return get_fisheries_dataset_summary()

@router.get("/fisheries/model-status")
def get_fisheries_model_status():
    metadata_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "models", "fisheries_catch_model_metadata.json"))
    if not os.path.exists(metadata_path):
        return {"status": "NOT_TRAINED", "model": "fisheries_catch_model.pkl"}
    with open(metadata_path, "r", encoding="utf-8") as metadata_file:
        return {"status": "TRAINED", **__import__("json").load(metadata_file)}

@router.get("/ecosystem/model-status")
def get_ecosystem_model_status():
    return EcosystemClimateDataset.model_status()

# ─────────────────────────────────────────────────────────────────────────────
# NOTIFICATION SERVICES — Email, SMS & Push
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/notifications/send", response_model=NotificationResponse)
def send_notification(req: NotificationSendRequest, db: Session = Depends(get_db)):
    """
    Send a notification through a specific channel (EMAIL, SMS, or PUSH).
    The notification is persisted in the audit log regardless of delivery outcome.
    """
    result = notification_dispatcher.send(
        channel=req.channel.value,
        recipient=req.recipient,
        body=req.body,
        subject=req.subject,
        severity=req.severity.value,
        location_name=req.location_name,
        location_lat=req.location_lat,
        location_lon=req.location_lon,
        metadata=req.metadata,
        db=db,
        notification_type=req.notification_type.value,
    )
    return NotificationResponse(
        status=result["status"],
        channel=result["channel"],
        recipient=result["recipient"],
        message_id=result.get("message_id"),
        timestamp=result["timestamp"],
        error=result.get("error"),
        demo_mode=result.get("demo_mode", False),
    )


@router.post("/notifications/send-bulk", response_model=NotificationBulkResponse)
def send_bulk_notification(req: NotificationBulkRequest, db: Session = Depends(get_db)):
    """
    Broadcast a notification to all users matching the target persona filter.
    Uses severity-based auto-escalation to determine channels.
    """
    # Query matching users
    query = db.query(UserDB).filter(UserDB.is_active == True)
    if req.target_persona != "ALL":
        query = query.filter(UserDB.role == req.target_persona)
    users = query.all()

    results = []
    sent_count = 0
    failed_count = 0
    demo_count = 0

    for user in users:
        user_results = notification_dispatcher.send_auto_escalated(
            recipient_email=user.email if user.notification_email else None,
            recipient_phone=user.phone_number if user.notification_sms and user.phone_number else None,
            recipient_fcm_token=user.fcm_token if user.notification_push and user.fcm_token else None,
            subject=req.subject,
            body=req.body,
            severity=req.severity.value,
            location_name=req.location_name,
            location_lat=req.location_lat,
            location_lon=req.location_lon,
            db=db,
            user_id=user.id,
            notification_type=req.notification_type.value,
        )
        for r in user_results:
            resp = NotificationResponse(
                status=r["status"],
                channel=r["channel"],
                recipient=r["recipient"],
                message_id=r.get("message_id"),
                timestamp=r["timestamp"],
                error=r.get("error"),
                demo_mode=r.get("demo_mode", False),
            )
            results.append(resp)
            if r["status"] == "SENT":
                sent_count += 1
            elif r["status"] == "FAILED":
                failed_count += 1
            elif r["status"] == "DEMO":
                demo_count += 1

    return NotificationBulkResponse(
        total_recipients=len(users),
        sent=sent_count,
        failed=failed_count,
        demo=demo_count,
        results=results,
    )


@router.post("/notifications/test", response_model=NotificationResponse)
def test_notification_channel(req: NotificationTestRequest, db: Session = Depends(get_db)):
    """
    Send a test notification to verify that a specific channel is configured correctly.
    """
    test_subject = "🧪 VARUNA Test Notification"
    test_body = (
        "This is a test notification from the VARUNA Marine Intelligence Platform.\n"
        "If you received this, the notification channel is working correctly.\n"
        f"Channel: {req.channel.value} | Timestamp: {datetime.now(timezone.utc).isoformat()}"
    )

    result = notification_dispatcher.send(
        channel=req.channel.value,
        recipient=req.recipient,
        body=test_body,
        subject=test_subject,
        severity="INFO",
        db=db,
        notification_type="TEST",
    )
    return NotificationResponse(
        status=result["status"],
        channel=result["channel"],
        recipient=result["recipient"],
        message_id=result.get("message_id"),
        timestamp=result["timestamp"],
        error=result.get("error"),
        demo_mode=result.get("demo_mode", False),
    )


@router.get("/notifications/history", response_model=NotificationHistoryResponse)
def get_notification_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    channel: Optional[str] = Query(None, description="Filter by channel: EMAIL, SMS, PUSH"),
    severity: Optional[str] = Query(None, description="Filter by severity: INFO, WARNING, CRITICAL"),
    status: Optional[str] = Query(None, description="Filter by status: SENT, FAILED, DEMO"),
    db: Session = Depends(get_db),
):
    """
    Retrieve paginated notification delivery history with optional filters.
    """
    query = db.query(NotificationDB)
    if channel:
        query = query.filter(NotificationDB.channel == channel.upper())
    if severity:
        query = query.filter(NotificationDB.severity == severity.upper())
    if status:
        query = query.filter(NotificationDB.status == status.upper())

    total = query.count()
    records = (
        query.order_by(NotificationDB.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items = [
        NotificationHistoryItem(
            id=r.id,
            channel=r.channel,
            recipient=r.recipient,
            subject=r.subject,
            body=r.body[:500],
            severity=r.severity,
            status=r.status,
            notification_type=r.notification_type or "GENERAL",
            message_id=r.message_id,
            error_detail=r.error_detail,
            location_name=r.location_name,
            created_at=r.created_at.isoformat() if r.created_at else "",
        )
        for r in records
    ]

    return NotificationHistoryResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items,
    )


@router.get("/notifications/channels/status", response_model=NotificationChannelsStatusResponse)
def get_notification_channels_status():
    """
    Health check for all notification channels (Email, SMS, Push).
    Reports whether each channel is OPERATIONAL, DEMO, or UNAVAILABLE.
    """
    status = notification_dispatcher.get_channels_status()
    return NotificationChannelsStatusResponse(
        email=ChannelHealthItem(**status["email"]),
        sms=ChannelHealthItem(**status["sms"]),
        push=ChannelHealthItem(**status["push"]),
        overall_status=status["overall_status"],
    )


@router.put("/notifications/preferences")
def update_notification_preferences(req: NotificationPreferenceUpdate, db: Session = Depends(get_db)):
    """
    Update a user's notification preferences (enabled channels, severity threshold, phone number).
    """
    user = db.query(UserDB).filter(UserDB.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if req.email_enabled is not None:
        user.notification_email = req.email_enabled
    if req.sms_enabled is not None:
        user.notification_sms = req.sms_enabled
    if req.push_enabled is not None:
        user.notification_push = req.push_enabled
    if req.severity_threshold is not None:
        user.notification_severity_threshold = req.severity_threshold.value
    if req.phone_number is not None:
        user.phone_number = req.phone_number

    db.commit()
    db.refresh(user)

    return {
        "status": "UPDATED",
        "user_id": user.id,
        "username": user.username,
        "notification_email": user.notification_email,
        "notification_sms": user.notification_sms,
        "notification_push": user.notification_push,
        "notification_severity_threshold": user.notification_severity_threshold,
        "phone_number": user.phone_number,
        "fcm_token": "configured" if user.fcm_token else "not set",
    }


@router.post("/notifications/register-device")
def register_fcm_device(req: DeviceRegistrationRequest, db: Session = Depends(get_db)):
    """
    Register or update an FCM device token for push notifications.
    """
    user = db.query(UserDB).filter(UserDB.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.fcm_token = req.fcm_token
    db.commit()

    return {
        "status": "REGISTERED",
        "user_id": user.id,
        "username": user.username,
        "fcm_token_prefix": req.fcm_token[:20] + "...",
        "device_info": req.device_info,
    }


@router.post("/notifications/trigger/risk-alert", response_model=NotificationBulkResponse)
def trigger_risk_alert_notification(req: RiskAlertTriggerRequest, db: Session = Depends(get_db)):
    """
    Trigger risk-based notifications from a location analysis result.
    Sends to all active users matching the target persona, using severity
    auto-escalation (SAFE→INFO/Push, CAUTION→WARNING/Push+Email, DANGER→CRITICAL/All channels).
    """
    severity_map = {"SAFE": "INFO", "CAUTION": "WARNING", "DANGER": "CRITICAL"}
    severity = severity_map.get(req.risk_level, "INFO")

    # Build the alert message
    subject = f"Marine Risk Alert: {req.risk_level} at {req.location_name or 'Unknown Location'}"
    body = (
        f"🌊 VARUNA Marine Risk Alert\n\n"
        f"Risk Level: {req.risk_level} (Score: {req.risk_score}/100)\n"
        f"Location: {req.location_name or 'N/A'} ({req.latitude}°N, {req.longitude}°E)\n\n"
    )
    if req.key_risks:
        body += "Key Risks:\n" + "\n".join(f"• {r}" for r in req.key_risks[:5]) + "\n\n"
    if req.recommendations:
        body += "Recommendations:\n" + "\n".join(f"→ {r}" for r in req.recommendations[:3])

    # Query matching users
    query = db.query(UserDB).filter(UserDB.is_active == True)
    if req.target_persona != "ALL":
        query = query.filter(UserDB.role == req.target_persona)
    users = query.all()

    results = []
    sent_count = 0
    failed_count = 0
    demo_count = 0

    for user in users:
        user_results = notification_dispatcher.send_auto_escalated(
            recipient_email=user.email if user.notification_email else None,
            recipient_phone=user.phone_number if user.notification_sms and user.phone_number else None,
            recipient_fcm_token=user.fcm_token if user.notification_push and user.fcm_token else None,
            subject=subject,
            body=body,
            severity=severity,
            location_name=req.location_name,
            location_lat=req.latitude,
            location_lon=req.longitude,
            metadata={"risk_level": req.risk_level, "risk_score": req.risk_score},
            db=db,
            user_id=user.id,
            notification_type="RISK_ALERT",
        )
        for r in user_results:
            resp = NotificationResponse(
                status=r["status"],
                channel=r["channel"],
                recipient=r["recipient"],
                message_id=r.get("message_id"),
                timestamp=r["timestamp"],
                error=r.get("error"),
                demo_mode=r.get("demo_mode", False),
            )
            results.append(resp)
            if r["status"] == "SENT":
                sent_count += 1
            elif r["status"] == "FAILED":
                failed_count += 1
            elif r["status"] == "DEMO":
                demo_count += 1

    return NotificationBulkResponse(
        total_recipients=len(users),
        sent=sent_count,
        failed=failed_count,
        demo=demo_count,
        results=results,
    )
