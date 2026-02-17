"""
WhatsApp service using Twilio.
Falls back to logging when Twilio is not configured.
"""

import logging
from config import Config
from services.circuit_breaker import get_breaker

logger = logging.getLogger("services.whatsapp")


class WhatsAppService:
    """Send WhatsApp messages via Twilio, or log them when not configured."""

    def __init__(self):
        self.configured = Config.is_whatsapp_configured()
        self.from_number = Config.TWILIO_WHATSAPP_FROM

        if self.configured:
            try:
                from twilio.rest import Client
                self.client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
                logger.info("Twilio WhatsApp service configured")
            except ImportError:
                logger.warning(
                    "twilio package not installed. Run: pip install twilio"
                )
                self.configured = False
                self.client = None
        else:
            logger.info("Twilio not configured. WhatsApp messages will be logged only.")
            self.client = None

    def send(self, to_phone: str, message: str) -> dict:
        """
        Send a WhatsApp message.
        to_phone should be in format like '972501234567' (no + prefix needed, we add it).
        """
        # Normalize phone number for WhatsApp
        wa_to = self._normalize_phone(to_phone)

        if not self.configured or not self.client:
            logger.info(
                f"[DRY RUN] WhatsApp to {wa_to}\n"
                f"  Message: {message[:200]}..."
            )
            return {
                "success": True,
                "dry_run": True,
                "message": "WhatsApp logged (Twilio not configured)",
            }

        breaker = get_breaker("twilio")
        if not breaker.is_closed():
            logger.warning("Twilio circuit breaker OPEN -- skipping WhatsApp")
            return {"success": False, "error": "Service temporarily unavailable (circuit breaker open)"}

        import time

        last_error = None
        for attempt in range(3):
            try:
                msg = self.client.messages.create(
                    body=message,
                    from_=self.from_number,
                    to=f"whatsapp:{wa_to}",
                )
                logger.info(f"WhatsApp sent to {wa_to}, SID: {msg.sid}")
                breaker.record_success()
                return {"success": True, "sid": msg.sid}
            except Exception as e:
                last_error = e
                err_str = str(e).lower()
                if "429" in str(e) or "500" in str(e) or "timeout" in err_str:
                    delay = 1.0 * (2 ** attempt)
                    logger.warning(f"WhatsApp transient error (attempt {attempt+1}/3): {e}. Retrying in {delay}s...")
                    time.sleep(delay)
                    continue
                logger.error(f"Failed to send WhatsApp to {wa_to}: {e}")
                return {"success": False, "error": str(e)}

        breaker.record_failure()
        logger.error(f"WhatsApp failed after 3 retries: {last_error}")
        return {"success": False, "error": str(last_error)}

    def _normalize_phone(self, phone: str) -> str:
        """Convert Israeli phone formats to international format."""
        # Remove non-digit characters
        digits = "".join(c for c in phone if c.isdigit())

        # Israeli mobile: 05X -> +9725X
        if digits.startswith("05"):
            return f"+972{digits[1:]}"
        elif digits.startswith("9725"):
            return f"+{digits}"
        elif digits.startswith("+"):
            return phone
        return f"+{digits}"

    def is_available(self) -> bool:
        return self.configured
