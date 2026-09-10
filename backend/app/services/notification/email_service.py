"""
VARUNA Email Notification Service — SMTP-based marine alert email delivery.
Sends HTML-formatted emails with severity-based colour coding.
Falls back to console logging when SMTP credentials are not configured.
"""

import smtplib
import logging
import uuid
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from datetime import datetime, timezone

from app.core.config import settings

logger = logging.getLogger("varuna.notifications.email")


# ── Severity Colour Palette ──────────────────────────────────────────────────
SEVERITY_COLOURS = {
    "INFO": {"bg": "#0d6efd", "text": "#ffffff", "label": "ℹ️  INFORMATION"},
    "WARNING": {"bg": "#ffc107", "text": "#212529", "label": "⚠️  WARNING"},
    "CRITICAL": {"bg": "#dc3545", "text": "#ffffff", "label": "🚨 CRITICAL ALERT"},
}


class EmailNotificationService:
    """
    SMTP email notification service with HTML marine-alert templates.
    Gracefully falls back to logging when SMTP is not configured.
    """

    def __init__(self):
        self._configured = bool(settings.SMTP_HOST and settings.SMTP_USERNAME and settings.SMTP_PASSWORD)
        if self._configured:
            logger.info(f"Email service configured: {settings.SMTP_HOST}:{settings.SMTP_PORT}")
        else:
            logger.warning("Email service in DEMO mode — SMTP credentials not configured.")

    @property
    def is_configured(self) -> bool:
        return self._configured

    def send(
        self,
        to_email: str,
        subject: str,
        body: str,
        severity: str = "INFO",
        location_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Send an HTML-formatted marine alert email.
        Returns a dict with status, message_id, and optional error.
        """
        message_id = f"varuna-email-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.now(timezone.utc).isoformat()

        html_body = self._build_html(subject, body, severity, location_name, metadata)

        if not self._configured:
            logger.info(
                f"[DEMO EMAIL] To: {to_email} | Subject: {subject} | "
                f"Severity: {severity} | Body: {body[:120]}..."
            )
            return {
                "status": "DEMO",
                "channel": "EMAIL",
                "recipient": to_email,
                "message_id": message_id,
                "timestamp": timestamp,
                "error": None,
                "demo_mode": True,
            }

        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = settings.SMTP_FROM_EMAIL
            msg["To"] = to_email
            msg["Subject"] = f"[VARUNA {severity}] {subject}"
            msg["X-VARUNA-MessageID"] = message_id

            # Plain-text fallback
            msg.attach(MIMEText(body, "plain", "utf-8"))
            # Rich HTML version
            msg.attach(MIMEText(html_body, "html", "utf-8"))

            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
                if settings.SMTP_USE_TLS:
                    server.starttls()
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.sendmail(settings.SMTP_FROM_EMAIL, [to_email], msg.as_string())

            logger.info(f"Email sent to {to_email}: {message_id}")
            return {
                "status": "SENT",
                "channel": "EMAIL",
                "recipient": to_email,
                "message_id": message_id,
                "timestamp": timestamp,
                "error": None,
                "demo_mode": False,
            }

        except Exception as e:
            logger.error(f"Email send failed to {to_email}: {e}")
            return {
                "status": "FAILED",
                "channel": "EMAIL",
                "recipient": to_email,
                "message_id": message_id,
                "timestamp": timestamp,
                "error": str(e),
                "demo_mode": False,
            }

    def _build_html(
        self,
        subject: str,
        body: str,
        severity: str,
        location_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build a branded HTML email template for marine alerts."""
        colours = SEVERITY_COLOURS.get(severity, SEVERITY_COLOURS["INFO"])
        loc_html = f'<p style="color:#6c757d;font-size:13px;">📍 Location: <strong>{location_name}</strong></p>' if location_name else ""

        meta_rows = ""
        if metadata:
            for k, v in metadata.items():
                meta_rows += f"<tr><td style='padding:4px 8px;color:#6c757d;font-size:13px;'>{k}</td><td style='padding:4px 8px;font-size:13px;'><strong>{v}</strong></td></tr>"

        meta_html = f"<table style='width:100%;border-collapse:collapse;margin-top:12px;'>{meta_rows}</table>" if meta_rows else ""

        body_html = body.replace("\n", "<br>")

        return f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f4f6f8;font-family:'Segoe UI',Roboto,Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f6f8;padding:24px 0;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08);">
        <!-- Header -->
        <tr>
          <td style="background:linear-gradient(135deg,#0a1628,#1a365d);padding:24px 32px;">
            <h1 style="margin:0;color:#ffffff;font-size:22px;">🌊 VARUNA Marine Intelligence</h1>
            <p style="margin:4px 0 0;color:#90cdf4;font-size:13px;">AI-Powered Marine Safety Platform — SIH 2026</p>
          </td>
        </tr>
        <!-- Severity Banner -->
        <tr>
          <td style="background:{colours['bg']};padding:14px 32px;">
            <span style="color:{colours['text']};font-size:16px;font-weight:700;">{colours['label']}</span>
          </td>
        </tr>
        <!-- Content -->
        <tr>
          <td style="padding:28px 32px;">
            <h2 style="margin:0 0 12px;color:#1a202c;font-size:18px;">{subject}</h2>
            {loc_html}
            <p style="color:#2d3748;font-size:14px;line-height:1.7;">{body_html}</p>
            {meta_html}
          </td>
        </tr>
        <!-- Footer -->
        <tr>
          <td style="background:#f7fafc;padding:16px 32px;border-top:1px solid #e2e8f0;">
            <p style="margin:0;color:#a0aec0;font-size:11px;">
              This is an automated alert from VARUNA Marine Intelligence Platform.
              Do not reply to this email. For official advisories, refer to INCOIS / IMD bulletins.
            </p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


# ── Module-level singleton ───────────────────────────────────────────────────
email_service = EmailNotificationService()
