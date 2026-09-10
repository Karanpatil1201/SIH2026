"""
VARUNA SMS Notification Service — Twilio REST API integration for marine safety SMS alerts.
Sends concise marine safety messages with severity prefix.
Falls back to console logging when Twilio credentials are not configured.
Uses httpx (no Twilio SDK dependency) for lightweight HTTP calls.
"""

import logging
import uuid
import base64
from typing import Optional, Dict, Any
from datetime import datetime, timezone

from app.core.config import settings

logger = logging.getLogger("varuna.notifications.sms")

TWILIO_API_BASE = "https://api.twilio.com/2010-04-01"

# Severity prefixes for SMS (kept short for 160-char segments)
SEVERITY_PREFIX = {
    "INFO": "ℹ️ VARUNA INFO",
    "WARNING": "⚠️ VARUNA WARNING",
    "CRITICAL": "🚨 VARUNA CRITICAL",
}


class SMSNotificationService:
    """
    Twilio-backed SMS notification service for marine safety alerts.
    Gracefully falls back to logging when Twilio credentials are not configured.
    """

    def __init__(self):
        self._configured = bool(
            settings.TWILIO_ACCOUNT_SID
            and settings.TWILIO_AUTH_TOKEN
            and settings.TWILIO_FROM_NUMBER
        )
        if self._configured:
            logger.info(f"SMS service configured via Twilio (SID: {settings.TWILIO_ACCOUNT_SID[:8]}...)")
        else:
            logger.warning("SMS service in DEMO mode — Twilio credentials not configured.")

    @property
    def is_configured(self) -> bool:
        return self._configured

    def send(
        self,
        to_number: str,
        body: str,
        severity: str = "INFO",
        location_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Send an SMS marine alert via Twilio REST API.
        Returns a dict with status, message_id, and optional error.
        """
        message_id = f"varuna-sms-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.now(timezone.utc).isoformat()

        # Build concise SMS body
        prefix = SEVERITY_PREFIX.get(severity, SEVERITY_PREFIX["INFO"])
        loc_tag = f" @ {location_name}" if location_name else ""
        sms_body = f"{prefix}{loc_tag}: {body}"

        # Truncate to ~450 chars (3 SMS segments max) to avoid excessive billing
        if len(sms_body) > 450:
            sms_body = sms_body[:447] + "..."

        if not self._configured:
            logger.info(
                f"[DEMO SMS] To: {to_number} | Severity: {severity} | "
                f"Body: {sms_body[:120]}..."
            )
            return {
                "status": "DEMO",
                "channel": "SMS",
                "recipient": to_number,
                "message_id": message_id,
                "timestamp": timestamp,
                "error": None,
                "demo_mode": True,
            }

        try:
            import httpx

            url = f"{TWILIO_API_BASE}/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages.json"
            auth_str = f"{settings.TWILIO_ACCOUNT_SID}:{settings.TWILIO_AUTH_TOKEN}"
            auth_header = base64.b64encode(auth_str.encode()).decode()

            response = httpx.post(
                url,
                headers={
                    "Authorization": f"Basic {auth_header}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data={
                    "From": settings.TWILIO_FROM_NUMBER,
                    "To": to_number,
                    "Body": sms_body,
                },
                timeout=15.0,
            )

            if response.status_code in (200, 201):
                resp_data = response.json()
                twilio_sid = resp_data.get("sid", message_id)
                logger.info(f"SMS sent to {to_number}: {twilio_sid}")
                return {
                    "status": "SENT",
                    "channel": "SMS",
                    "recipient": to_number,
                    "message_id": twilio_sid,
                    "timestamp": timestamp,
                    "error": None,
                    "demo_mode": False,
                }
            else:
                error_msg = f"Twilio HTTP {response.status_code}: {response.text[:200]}"
                logger.error(f"SMS send failed to {to_number}: {error_msg}")
                return {
                    "status": "FAILED",
                    "channel": "SMS",
                    "recipient": to_number,
                    "message_id": message_id,
                    "timestamp": timestamp,
                    "error": error_msg,
                    "demo_mode": False,
                }

        except ImportError:
            logger.error("httpx not installed. Run: pip install httpx")
            return {
                "status": "FAILED",
                "channel": "SMS",
                "recipient": to_number,
                "message_id": message_id,
                "timestamp": timestamp,
                "error": "httpx package not installed",
                "demo_mode": False,
            }
        except Exception as e:
            logger.error(f"SMS send failed to {to_number}: {e}")
            return {
                "status": "FAILED",
                "channel": "SMS",
                "recipient": to_number,
                "message_id": message_id,
                "timestamp": timestamp,
                "error": str(e),
                "demo_mode": False,
            }


# ── Module-level singleton ───────────────────────────────────────────────────
sms_service = SMSNotificationService()
