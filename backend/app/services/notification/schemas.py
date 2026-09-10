"""
VARUNA Notification Schemas — Pydantic models for notification requests, responses,
preferences, and history items used across all notification channels.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class NotificationChannel(str, Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"
    PUSH = "PUSH"


class NotificationSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class NotificationStatus(str, Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"
    DEMO = "DEMO"


class NotificationType(str, Enum):
    GENERAL = "GENERAL"
    RISK_ALERT = "RISK_ALERT"
    CYCLONE = "CYCLONE"
    ADVISORY = "ADVISORY"
    PFZ = "PFZ"
    TEST = "TEST"


# ── Request Models ───────────────────────────────────────────────────────────

class NotificationSendRequest(BaseModel):
    """Request to send a notification through one or more channels."""
    channel: NotificationChannel = Field(..., description="Delivery channel: EMAIL, SMS, or PUSH")
    recipient: str = Field(..., description="Email address, phone number, or FCM device token")
    subject: Optional[str] = Field(None, description="Subject line (primarily for email)")
    body: str = Field(..., description="Notification message body")
    severity: NotificationSeverity = Field(default=NotificationSeverity.INFO, description="Alert severity level")
    notification_type: NotificationType = Field(default=NotificationType.GENERAL)
    location_lat: Optional[float] = Field(None, ge=-90.0, le=90.0)
    location_lon: Optional[float] = Field(None, ge=-180.0, le=180.0)
    location_name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class NotificationBulkRequest(BaseModel):
    """Request to broadcast notifications to users matching a filter."""
    subject: str = Field(..., description="Notification subject")
    body: str = Field(..., description="Notification message body")
    severity: NotificationSeverity = Field(default=NotificationSeverity.WARNING)
    notification_type: NotificationType = Field(default=NotificationType.GENERAL)
    target_persona: str = Field(default="ALL", description="Target user role: ALL, Fisherman, Shipping, etc.")
    channels: List[NotificationChannel] = Field(
        default=[NotificationChannel.PUSH],
        description="Channels to use. If empty, auto-escalation based on severity applies."
    )
    location_lat: Optional[float] = None
    location_lon: Optional[float] = None
    location_name: Optional[str] = None


class NotificationTestRequest(BaseModel):
    """Request to send a test notification to verify channel configuration."""
    channel: NotificationChannel = Field(..., description="Channel to test")
    recipient: str = Field(..., description="Test recipient address/number/token")


class RiskAlertTriggerRequest(BaseModel):
    """Trigger a risk-based notification from a location analysis."""
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    risk_level: str = Field(..., description="SAFE, CAUTION, or DANGER")
    risk_score: float = Field(..., ge=0.0, le=100.0)
    location_name: Optional[str] = None
    key_risks: List[str] = Field(default=[])
    recommendations: List[str] = Field(default=[])
    target_persona: str = Field(default="ALL")


class DeviceRegistrationRequest(BaseModel):
    """Register an FCM device token for push notifications."""
    user_id: int = Field(..., description="User ID to associate the device token with")
    fcm_token: str = Field(..., description="Firebase Cloud Messaging device token")
    device_info: Optional[str] = Field(None, description="Optional device name/type")


class NotificationPreferenceUpdate(BaseModel):
    """Update user notification preferences."""
    user_id: int
    email_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    severity_threshold: Optional[NotificationSeverity] = None
    phone_number: Optional[str] = None


# ── Response Models ──────────────────────────────────────────────────────────

class NotificationResponse(BaseModel):
    """Response after sending a single notification."""
    status: NotificationStatus
    channel: NotificationChannel
    recipient: str
    message_id: Optional[str] = None
    timestamp: str
    error: Optional[str] = None
    demo_mode: bool = False


class NotificationBulkResponse(BaseModel):
    """Response after sending bulk notifications."""
    total_recipients: int
    sent: int
    failed: int
    demo: int
    results: List[NotificationResponse]


class NotificationHistoryItem(BaseModel):
    """A single notification log entry."""
    id: int
    channel: str
    recipient: str
    subject: Optional[str]
    body: str
    severity: str
    status: str
    notification_type: str
    message_id: Optional[str]
    error_detail: Optional[str]
    location_name: Optional[str]
    created_at: str


class NotificationHistoryResponse(BaseModel):
    """Paginated notification history."""
    total: int
    page: int
    page_size: int
    items: List[NotificationHistoryItem]


class ChannelHealthItem(BaseModel):
    """Health status for a single notification channel."""
    channel: str
    status: str  # OPERATIONAL, DEMO, UNAVAILABLE
    provider: str
    configured: bool
    details: str


class NotificationChannelsStatusResponse(BaseModel):
    """Health status for all notification channels."""
    email: ChannelHealthItem
    sms: ChannelHealthItem
    push: ChannelHealthItem
    overall_status: str  # OPERATIONAL, PARTIAL, DEMO
