"""
VARUNA Notification Dispatcher — Central orchestrator for multi-channel notification delivery.
Routes notifications to Email, SMS, and/or Push channels based on severity auto-escalation
and user preferences. Persists every attempt in NotificationDB for audit trail.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.notification.email_service import email_service
from app.services.notification.sms_service import sms_service
from app.services.notification.push_service import push_service

logger = logging.getLogger("varuna.notifications.dispatcher")

# ── Severity-Based Auto-Escalation Rules ─────────────────────────────────────
# INFO     → Push only
# WARNING  → Push + Email
# CRITICAL → Push + Email + SMS
SEVERITY_ESCALATION = {
    "INFO": ["PUSH"],
    "WARNING": ["PUSH", "EMAIL"],
    "CRITICAL": ["PUSH", "EMAIL", "SMS"],
}


class NotificationDispatcher:
    """
    Central notification dispatcher that orchestrates multi-channel delivery,
    applies severity-based auto-escalation, and records audit logs.
    """

    def __init__(self):
        self.email = email_service
        self.sms = sms_service
        self.push = push_service
        logger.info("NotificationDispatcher initialized.")

    # ── Single Notification ──────────────────────────────────────────────────

    def send(
        self,
        channel: str,
        recipient: str,
        body: str,
        subject: Optional[str] = None,
        severity: str = "INFO",
        location_name: Optional[str] = None,
        location_lat: Optional[float] = None,
        location_lon: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
        db: Optional[Session] = None,
        user_id: Optional[int] = None,
        notification_type: str = "GENERAL",
    ) -> Dict[str, Any]:
        """Send a notification through a specific channel."""
        channel = channel.upper()
        result = self._dispatch_to_channel(
            channel=channel,
            recipient=recipient,
            subject=subject or f"VARUNA {severity} Alert",
            body=body,
            severity=severity,
            location_name=location_name,
            location_lat=location_lat,
            location_lon=location_lon,
            metadata=metadata,
        )

        # Persist to DB
        if db:
            self._record_notification(
                db=db,
                user_id=user_id,
                channel=channel,
                recipient=recipient,
                subject=subject,
                body=body,
                severity=severity,
                status=result["status"],
                message_id=result.get("message_id"),
                error_detail=result.get("error"),
                location_lat=location_lat,
                location_lon=location_lon,
                location_name=location_name,
                notification_type=notification_type,
                metadata=metadata,
            )

        return result

    # ── Auto-Escalated Notification ──────────────────────────────────────────

    def send_auto_escalated(
        self,
        recipient_email: Optional[str] = None,
        recipient_phone: Optional[str] = None,
        recipient_fcm_token: Optional[str] = None,
        subject: str = "VARUNA Alert",
        body: str = "",
        severity: str = "INFO",
        location_name: Optional[str] = None,
        location_lat: Optional[float] = None,
        location_lon: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
        db: Optional[Session] = None,
        user_id: Optional[int] = None,
        notification_type: str = "GENERAL",
    ) -> List[Dict[str, Any]]:
        """
        Send notifications across channels based on severity auto-escalation.
        INFO → Push | WARNING → Push + Email | CRITICAL → Push + Email + SMS
        """
        channels = SEVERITY_ESCALATION.get(severity, ["PUSH"])
        results = []

        for channel in channels:
            if channel == "PUSH" and recipient_fcm_token:
                result = self.send(
                    channel="PUSH", recipient=recipient_fcm_token,
                    body=body, subject=subject, severity=severity,
                    location_name=location_name, location_lat=location_lat,
                    location_lon=location_lon, metadata=metadata, db=db,
                    user_id=user_id, notification_type=notification_type,
                )
                results.append(result)

            elif channel == "EMAIL" and recipient_email:
                result = self.send(
                    channel="EMAIL", recipient=recipient_email,
                    body=body, subject=subject, severity=severity,
                    location_name=location_name, location_lat=location_lat,
                    location_lon=location_lon, metadata=metadata, db=db,
                    user_id=user_id, notification_type=notification_type,
                )
                results.append(result)

            elif channel == "SMS" and recipient_phone:
                result = self.send(
                    channel="SMS", recipient=recipient_phone,
                    body=body, subject=subject, severity=severity,
                    location_name=location_name, location_lat=location_lat,
                    location_lon=location_lon, metadata=metadata, db=db,
                    user_id=user_id, notification_type=notification_type,
                )
                results.append(result)

        return results

    # ── Risk Alert Convenience Method ────────────────────────────────────────

    def send_risk_alert(
        self,
        risk_level: str,
        risk_score: float,
        location_name: str,
        latitude: float,
        longitude: float,
        key_risks: List[str],
        recommendations: List[str],
        recipient_email: Optional[str] = None,
        recipient_phone: Optional[str] = None,
        recipient_fcm_token: Optional[str] = None,
        db: Optional[Session] = None,
        user_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Build and send a risk-based alert with auto-escalation."""
        severity_map = {"SAFE": "INFO", "CAUTION": "WARNING", "DANGER": "CRITICAL"}
        severity = severity_map.get(risk_level, "INFO")

        subject = f"Marine Risk Alert: {risk_level} at {location_name}"
        body = (
            f"Risk Level: {risk_level} (Score: {risk_score}/100)\n"
            f"Location: {location_name} ({latitude}°N, {longitude}°E)\n\n"
            f"Key Risks:\n" + "\n".join(f"• {r}" for r in key_risks[:5]) + "\n\n"
            f"Recommendations:\n" + "\n".join(f"→ {r}" for r in recommendations[:3])
        )

        metadata = {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "notification_type": "RISK_ALERT",
        }

        return self.send_auto_escalated(
            recipient_email=recipient_email,
            recipient_phone=recipient_phone,
            recipient_fcm_token=recipient_fcm_token,
            subject=subject,
            body=body,
            severity=severity,
            location_name=location_name,
            location_lat=latitude,
            location_lon=longitude,
            metadata=metadata,
            db=db,
            user_id=user_id,
            notification_type="RISK_ALERT",
        )

    # ── Cyclone Warning Convenience Method ───────────────────────────────────

    def send_cyclone_warning(
        self,
        cyclone_name: str,
        category: str,
        current_location: Dict[str, float],
        affected_ports: List[str],
        max_wind_kmh: float,
        recipient_email: Optional[str] = None,
        recipient_phone: Optional[str] = None,
        recipient_fcm_token: Optional[str] = None,
        db: Optional[Session] = None,
        user_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Build and send a cyclone warning alert (always CRITICAL)."""
        subject = f"🌀 Cyclone Alert: {cyclone_name} — {category}"
        body = (
            f"Cyclonic Storm '{cyclone_name}' — Category: {category}\n"
            f"Current Position: {current_location.get('lat', '?')}°N, {current_location.get('lon', '?')}°E\n"
            f"Max Sustained Winds: {max_wind_kmh} km/h\n\n"
            f"Affected Ports:\n" + "\n".join(f"• {p}" for p in affected_ports) + "\n\n"
            f"⚠️ IMMEDIATE ACTION: Seek shelter, secure vessels, monitor INCOIS/IMD bulletins."
        )

        return self.send_auto_escalated(
            recipient_email=recipient_email,
            recipient_phone=recipient_phone,
            recipient_fcm_token=recipient_fcm_token,
            subject=subject,
            body=body,
            severity="CRITICAL",
            location_name=cyclone_name,
            location_lat=current_location.get("lat"),
            location_lon=current_location.get("lon"),
            metadata={"notification_type": "CYCLONE", "category": category},
            db=db,
            user_id=user_id,
            notification_type="CYCLONE",
        )

    # ── Channel Health ───────────────────────────────────────────────────────

    def get_channels_status(self) -> Dict[str, Any]:
        """Return health/configuration status for all notification channels."""
        email_status = {
            "channel": "EMAIL",
            "status": "OPERATIONAL" if self.email.is_configured else "DEMO",
            "provider": "SMTP",
            "configured": self.email.is_configured,
            "details": f"SMTP via {settings.SMTP_HOST}:{settings.SMTP_PORT}" if self.email.is_configured else "Not configured — messages logged to console",
        }
        sms_status = {
            "channel": "SMS",
            "status": "OPERATIONAL" if self.sms.is_configured else "DEMO",
            "provider": "Twilio",
            "configured": self.sms.is_configured,
            "details": f"Twilio SID: {settings.TWILIO_ACCOUNT_SID[:8]}..." if self.sms.is_configured else "Not configured — messages logged to console",
        }
        push_status = {
            "channel": "PUSH",
            "status": "OPERATIONAL" if self.push.is_configured else "DEMO",
            "provider": "Firebase Cloud Messaging",
            "configured": self.push.is_configured,
            "details": "FCM server key configured" if self.push.is_configured else "Not configured — messages logged to console",
        }

        configured_count = sum([self.email.is_configured, self.sms.is_configured, self.push.is_configured])
        if configured_count == 3:
            overall = "OPERATIONAL"
        elif configured_count >= 1:
            overall = "PARTIAL"
        else:
            overall = "DEMO"

        return {
            "email": email_status,
            "sms": sms_status,
            "push": push_status,
            "overall_status": overall,
        }

    # ── Internal Helpers ─────────────────────────────────────────────────────

    def _dispatch_to_channel(
        self,
        channel: str,
        recipient: str,
        subject: str,
        body: str,
        severity: str,
        location_name: Optional[str] = None,
        location_lat: Optional[float] = None,
        location_lon: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Route to the correct channel service."""
        if channel == "EMAIL":
            return self.email.send(
                to_email=recipient,
                subject=subject,
                body=body,
                severity=severity,
                location_name=location_name,
                metadata=metadata,
            )
        elif channel == "SMS":
            return self.sms.send(
                to_number=recipient,
                body=body,
                severity=severity,
                location_name=location_name,
                metadata=metadata,
            )
        elif channel == "PUSH":
            return self.push.send(
                device_token=recipient,
                title=subject,
                body=body,
                severity=severity,
                location_name=location_name,
                location_lat=location_lat,
                location_lon=location_lon,
                metadata=metadata,
            )
        else:
            return {
                "status": "FAILED",
                "channel": channel,
                "recipient": recipient,
                "message_id": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": f"Unknown channel: {channel}",
                "demo_mode": False,
            }

    def _record_notification(
        self,
        db: Session,
        user_id: Optional[int],
        channel: str,
        recipient: str,
        subject: Optional[str],
        body: str,
        severity: str,
        status: str,
        message_id: Optional[str],
        error_detail: Optional[str],
        location_lat: Optional[float],
        location_lon: Optional[float],
        location_name: Optional[str],
        notification_type: str,
        metadata: Optional[Dict[str, Any]],
    ):
        """Persist a notification record to the database."""
        try:
            from app.models.database_models import NotificationDB

            record = NotificationDB(
                user_id=user_id,
                channel=channel,
                recipient=recipient,
                subject=subject,
                body=body[:2000],  # Truncate very long bodies
                severity=severity,
                status=status,
                message_id=message_id,
                error_detail=error_detail,
                location_lat=location_lat,
                location_lon=location_lon,
                location_name=location_name,
                notification_type=notification_type,
                metadata_json=metadata,
            )
            db.add(record)
            db.commit()
        except Exception as e:
            logger.error(f"Failed to persist notification record: {e}")
            db.rollback()


# ── Module-level singleton ───────────────────────────────────────────────────
notification_dispatcher = NotificationDispatcher()
