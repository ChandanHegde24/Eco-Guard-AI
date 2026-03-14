import logging
import smtplib
from email.message import EmailMessage

import requests

from core.config import settings

logger = logging.getLogger(__name__)


def _send_email(subject: str, body: str) -> bool:
    if not settings.ALERT_EMAIL_TO or not settings.SMTP_HOST:
        logger.info("Email alert skipped: SMTP or recipient not configured")
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM
    msg["To"] = settings.ALERT_EMAIL_TO
    msg.set_content(body)

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
            if settings.SMTP_STARTTLS:
                server.starttls()
            if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception:
        logger.exception("Failed to send email alert")
        return False


def _send_webhook(payload: dict) -> bool:
    if not settings.ALERT_WEBHOOK_URL:
        logger.info("Webhook alert skipped: URL not configured")
        return False

    try:
        response = requests.post(settings.ALERT_WEBHOOK_URL, json=payload, timeout=15)
        response.raise_for_status()
        return True
    except Exception:
        logger.exception("Failed to send webhook alert")
        return False


def dispatch_alert_if_needed(risk_report: dict, location_data: dict) -> bool:
    if not risk_report.get("trigger_alert"):
        return False

    subject = f"Eco-Guard Critical Alert: {risk_report.get('change_percentage', 0):.2f}% change"
    body = (
        "Critical environmental change detected.\n\n"
        f"Coordinates: {location_data}\n"
        f"Risk Level: {risk_report.get('risk_level')}\n"
        f"Action: {risk_report.get('action')}\n"
        f"Change: {risk_report.get('change_percentage')}%\n"
    )

    webhook_payload = {
        "event": "critical_environmental_change",
        "location": location_data,
        "risk": risk_report,
    }

    email_sent = _send_email(subject, body)
    webhook_sent = _send_webhook(webhook_payload)

    return email_sent or webhook_sent
