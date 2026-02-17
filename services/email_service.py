"""
Email service using SendGrid.
Falls back to logging when SendGrid is not configured.
"""

import logging
from typing import Optional

from config import Config
from services.circuit_breaker import get_breaker

logger = logging.getLogger("services.email")


class EmailService:
    """Send emails via SendGrid, or log them when not configured."""

    def __init__(self):
        self.configured = Config.is_email_configured()
        self.from_email = Config.SENDGRID_FROM_EMAIL

        if self.configured:
            try:
                import sendgrid  # noqa: F401
                self.sg = sendgrid.SendGridAPIClient(api_key=Config.SENDGRID_API_KEY)
                logger.info("SendGrid email service configured")
            except ImportError:
                logger.warning(
                    "sendgrid package not installed. Run: pip install sendgrid"
                )
                self.configured = False
                self.sg = None
        else:
            logger.info("SendGrid not configured. Emails will be logged only.")
            self.sg = None

    def send(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: Optional[str] = None,
    ) -> dict:
        """
        Send an email.
        Returns {"success": True/False, "message_id": ..., "status": ...}
        """
        if not self.configured or not self.sg:
            logger.info(
                f"[DRY RUN] Email to {to_email}\n"
                f"  Subject: {subject}\n"
                f"  Body: {body_text or body_html[:200]}..."
            )
            return {
                "success": True,
                "dry_run": True,
                "message": "Email logged (SendGrid not configured)",
            }

        breaker = get_breaker("sendgrid")
        if not breaker.is_closed():
            logger.warning("SendGrid circuit breaker OPEN -- skipping email")
            return {"success": False, "error": "Service temporarily unavailable (circuit breaker open)"}

        import time
        from sendgrid.helpers.mail import Mail

        last_error = None
        for attempt in range(3):
            try:
                message = Mail(
                    from_email=self.from_email,
                    to_emails=to_email,
                    subject=subject,
                    html_content=body_html,
                )
                if body_text:
                    message.plain_text_content = body_text

                response = self.sg.send(message)
                logger.info(f"Email sent to {to_email}, status: {response.status_code}")
                breaker.record_success()
                return {
                    "success": response.status_code in (200, 201, 202),
                    "status_code": response.status_code,
                }
            except Exception as e:
                last_error = e
                err_str = str(e).lower()
                if "429" in str(e) or "500" in str(e) or "502" in str(e) or "503" in str(e) or "timeout" in err_str:
                    delay = 1.0 * (2 ** attempt)
                    logger.warning(f"Email send transient error (attempt {attempt+1}/3): {e}. Retrying in {delay}s...")
                    time.sleep(delay)
                    continue
                logger.error(f"Failed to send email to {to_email}: {e}")
                return {"success": False, "error": str(e)}

        breaker.record_failure()
        logger.error(f"Failed to send email after 3 retries: {last_error}")
        return {"success": False, "error": str(last_error)}

    def is_available(self) -> bool:
        return self.configured
