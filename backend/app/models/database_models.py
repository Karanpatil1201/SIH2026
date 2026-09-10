import uuid
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON, ForeignKey, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func
from app.core.database import Base

class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses String.
    """
    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=False))
        else:
            return dialect.type_descriptor(String())

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return str(value)

class UserDB(Base):
    __tablename__ = "users"
    id = Column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="Fisherman") # Fisherman, Shipping, Disaster Management, Researcher, Government
    full_name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    fcm_token = Column(String, nullable=True)
    notification_email = Column(Boolean, default=True)
    notification_sms = Column(Boolean, default=True)
    notification_push = Column(Boolean, default=True)
    notification_severity_threshold = Column(String, default="INFO") # INFO, WARNING, CRITICAL
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class MarineObservationDB(Base):
    __tablename__ = "marine_observations"
    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, index=True, nullable=False)
    longitude = Column(Float, index=True, nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)
    sst = Column(Float, nullable=True)
    wave_height = Column(Float, nullable=True)
    wave_direction = Column(Float, nullable=True)
    wave_period = Column(Float, nullable=True)
    swell_height = Column(Float, nullable=True)
    current_velocity = Column(Float, nullable=True)
    current_direction = Column(Float, nullable=True)
    salinity = Column(Float, nullable=True)
    chlorophyll = Column(Float, nullable=True)
    sea_level = Column(Float, nullable=True)
    source = Column(String, default="Copernicus")
    quality_score = Column(Float, default=100.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class WeatherObservationDB(Base):
    __tablename__ = "weather_observations"
    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, index=True, nullable=False)
    longitude = Column(Float, index=True, nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)
    wind_speed = Column(Float, nullable=True)
    wind_direction = Column(Float, nullable=True)
    air_temperature = Column(Float, nullable=True)
    pressure = Column(Float, nullable=True)
    precipitation = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    cloud_cover = Column(Float, nullable=True)
    source = Column(String, default="Open-Meteo Weather")
    quality_score = Column(Float, default=100.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class RiskAssessmentDB(Base):
    __tablename__ = "risk_assessments"
    id = Column(Integer, primary_key=True, index=True)
    location_name = Column(String, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    risk_score = Column(Float, nullable=False) # 0 - 100
    risk_level = Column(String, nullable=False) # LOW, MODERATE, HIGH, CRITICAL
    confidence = Column(Float, nullable=False) # 0 - 1.0
    uncertainty_level = Column(String, nullable=False) # Low, Moderate, High
    shap_explanation = Column(JSON, nullable=True)
    fused_features = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AdvisoryDB(Base):
    __tablename__ = "advisories"
    id = Column(Integer, primary_key=True, index=True)
    advisory_id = Column(String, unique=True, index=True)
    source = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    issue_time = Column(DateTime, nullable=False)
    expiry_time = Column(DateTime, nullable=False)
    affected_region = Column(String, nullable=False)
    severity = Column(String, nullable=False) # INFO, WARNING, SEVERE, CRITICAL
    confidence = Column(Float, default=0.9)
    status = Column(String, default="ACTIVE")
    source_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AlertDB(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String, nullable=False) # INFO, WATCH, WARNING, CRITICAL
    target_persona = Column(String, default="ALL")
    location_name = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    timestamp = Column(DateTime, server_default=func.now())
    is_read = Column(Boolean, default=False)

class FeedbackDB(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(GUID, ForeignKey("users.id"), nullable=True)
    persona = Column(String, nullable=False)
    query_or_prediction_id = Column(String, nullable=True)
    feedback_type = Column(String, nullable=False) # CORRECT, INCORRECT, FALSE_ALERT, MISSED_EVENT
    comments = Column(Text, nullable=True)
    status = Column(String, default="PENDING_REVIEW") # PENDING_REVIEW, VALIDATED, ARCHIVED
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SimulationRunDB(Base):
    __tablename__ = "simulation_runs"
    id = Column(Integer, primary_key=True, index=True)
    scenario_name = Column(String, nullable=False)
    parameters = Column(JSON, nullable=False)
    original_risk = Column(Float, nullable=False)
    simulated_risk = Column(Float, nullable=False)
    risk_delta = Column(Float, nullable=False)
    affected_zones = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class RAGDocumentDB(Base):
    __tablename__ = "rag_documents"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False) # INCOIS, CYCLONE, NAVIGATION, RESEARCH
    content = Column(Text, nullable=False)
    source_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class NotificationDB(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(GUID, ForeignKey("users.id"), nullable=True)
    channel = Column(String, nullable=False)  # EMAIL, SMS, PUSH
    recipient = Column(String, nullable=False)  # email address, phone number, or FCM token
    subject = Column(String, nullable=True)
    body = Column(Text, nullable=False)
    severity = Column(String, default="INFO")  # INFO, WARNING, CRITICAL
    status = Column(String, default="PENDING")  # PENDING, SENT, FAILED, DEMO
    message_id = Column(String, nullable=True)
    error_detail = Column(Text, nullable=True)
    location_lat = Column(Float, nullable=True)
    location_lon = Column(Float, nullable=True)
    location_name = Column(String, nullable=True)
    notification_type = Column(String, default="GENERAL")  # GENERAL, RISK_ALERT, CYCLONE, ADVISORY, PFZ, TEST
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class OTPChallengeDB(Base):
    __tablename__ = "otp_challenges"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True, nullable=False)
    code_hash = Column(String, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    consumed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserSessionDB(Base):
    __tablename__ = "user_sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(GUID, ForeignKey("users.id"), nullable=False)
    login_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    logout_time = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class QueryHistoryDB(Base):
    __tablename__ = "query_history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(GUID, ForeignKey("users.id"), nullable=False)
    query = Column(Text, nullable=False)
    language = Column(String, default="en")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    response_status = Column(String, default="SUCCESS") # SUCCESS, ERROR
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ActivityLogDB(Base):
    __tablename__ = "activity_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(GUID, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False) # LOGIN, LOGOUT, QUERY_RAG, QUERY_CHAT, UPDATE_PROFILE, etc.
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
