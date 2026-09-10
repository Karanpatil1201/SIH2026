"""
VARUNA Push Notification Service — Firebase Cloud Messaging (FCM) HTTP v1 integration.
Sends structured push payloads with severity-based icons and location data.
Falls back to console logging when FCM credentials are not configured.
"""

import logging
import uuid
from typing import Optional, Dict, Any
from datetime import datetime, timezone

from app.core.config import settings

logger = logging.getLogger("varuna.notifications.push")

FCM_SEND_URL = "https://fcm.googleapis.com/fcm/send"

# Severity-based notification config
SEVERITY_CONFIG = {
    "INFO": {"icon": "info_icon", "color": "#0d6efd", "priority": "normal", "sound": "default"},
    "WARNING": {"icon": "warning_icon", "color": "#ffc107", "priority": "high", "sound": "alert_warning.wav"},
    "CRITICAL": {"icon": "critical_icon", "color": "#dc3545", "priority": "high", "sound": "alert_critical.wav"},
}


class PushNotificationService:
    """
    Firebase Cloud Messaging push notification service for marine safety alerts.
    Gracefully falls back to logging when FCM credentials are not configured.
    """

    def __init__(self):
        self._configured = bool(settings.FCM_SERVER_KEY)
        if self._configured:
            logger.info("Push notification service configured via FCM.")
        else:
            logger.warning("Push service in DEMO mode — FCM_SERVER_KEY not configured.")

    @property
    def is_configured(self) -> bool:
        return self._configured

    def send(
        self,
        device_token: str,
        title: str,
        body: str,
        severity: str = "INFO",
        location_name: Optional[str] = None,
        location_lat: Optional[float] = None,
        location_lon: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Send a push notification via FCM legacy HTTP API.
        Returns a dict with status, message_id, and optional error.
        """
        message_id = f"varuna-push-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.now(timezone.utc).isoformat()

        config = SEVERITY_CONFIG.get(severity, SEVERITY_CONFIG["INFO"])

        # Build the structured payload
        data_payload = {
            "varuna_message_id": message_id,
            "severity": severity,
            "notification_type": (metadata or {}).get("notification_type", "GENERAL"),
            "click_action": "OPEN_VARUNA_DASHBOARD",
        }
        if location_name:
            data_payload["location_name"] = location_name
        if location_lat is not None:
            data_payload["location_lat"] = str(location_lat)
        if location_lon is not None:
            data_payload["location_lon"] = str(location_lon)
        if metadata:
            for k, v in metadata.items():
                if k not in data_payload:
                    data_payload[k] = str(v)

        if not self._configured:
            logger.info(
                f"[DEMO PUSH] Token: {device_token[:20]}... | Title: {title} | "
                f"Severity: {severity} | Body: {body[:100]}..."
            )
            return {
                "status": "DEMO",
                "channel": "PUSH",
                "recipient": device_token,
                "message_id": message_id,
                "timestamp": timestamp,
                "error": None,
                "demo_mode": True,
            }

        try:
            import httpx

            fcm_payload = {
                "to": device_token,
                "priority": config["priority"],
                "notification": {
                    "title": f"🌊 VARUNA | {title}",
                    "body": body,
                    "icon": config["icon"],
                    "color": config["color"],
                    "sound": config["sound"],
                    "click_action": "OPEN_VARUNA_DASHBOARD",
                },
                "data": data_payload,
            }

            response = httpx.post(
                FCM_SEND_URL,
                headers={
                    "Authorization": f"key={settings.FCM_SERVER_KEY}",
                    "Content-Type": "application/json",
                },
                json=fcm_payload,
                timeout=15.0,
            )

            if response.status_code == 200:
                resp_data = response.json()
                if resp_data.get("success", 0) >= 1:
                    logger.info(f"Push sent to token {device_token[:20]}...: {message_id}")
                    return {
                        "status": "SENT",
                        "channel": "PUSH",
                        "recipient": device_token,
                        "message_id": message_id,
                        "timestamp": timestamp,
                        "error": None,
                        "demo_mode": False,
                    }
                else:
                    error_msg = f"FCM delivery failure: {resp_data.get('results', [])}"
                    logger.error(f"Push delivery failed: {error_msg}")
                    return {
                        "status": "FAILED",
                        "channel": "PUSH",
                        "recipient": device_token,
                        "message_id": message_id,
                        "timestamp": timestamp,
                        "error": error_msg,
                        "demo_mode": False,
                    }
            else:
                error_msg = f"FCM HTTP {response.status_code}: {response.text[:200]}"
                logger.error(f"Push send failed: {error_msg}")
                return {
                    "status": "FAILED",
                    "channel": "PUSH",
                    "recipient": device_token,
                    "message_id": message_id,
                    "timestamp": timestamp,
                    "error": error_msg,
                    "demo_mode": False,
                }

        except ImportError:
            logger.error("httpx not installed. Run: pip install httpx")
            return {
                "status": "FAILED",
                "channel": "PUSH",
                "recipient": device_token,
                "message_id": message_id,
                "timestamp": timestamp,
                "error": "httpx package not installed",
                "demo_mode": False,
            }
        except Exception as e:
            logger.error(f"Push send failed: {e}")
            return {
                "status": "FAILED",
                "channel": "PUSH",
                "recipient": device_token,
                "message_id": message_id,
                "timestamp": timestamp,
                "error": str(e),
                "demo_mode": False,
            }

    def send_to_topic(
        self,
        topic: str,
        title: str,
        body: str,
        severity: str = "INFO",
    ) -> Dict[str, Any]:
        """
        Send a push notification to an FCM topic (e.g., 'fisherman_alerts').
        Useful for broadcasting to all users subscribed to a role-based topic.
        """
        topic_token = f"/topics/{topic}"
        return self.send(
            device_token=topic_token,
            title=title,
            body=body,
            severity=severity,
        )


# ── Module-level singleton ───────────────────────────────────────────────────
push_service = PushNotificationService()
