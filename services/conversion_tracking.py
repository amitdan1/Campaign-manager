"""
Conversion Tracking Service — sends server-side events to ad networks.

Supports:
- Facebook Conversions API (CAPI) — Lead, ConsultationBooked, Purchase events
- Google Ads Enhanced Conversions — offline conversion uploads

Server-side tracking is critical because iOS privacy changes (ATT) block
~40% of client-side pixel events. For service businesses with low lead
volumes (8-15/month), every conversion signal matters.
"""

import hashlib
import logging
import time
from typing import Any, Dict, Optional

import requests

from config import Config

logger = logging.getLogger("services.conversion_tracking")


def _hash_value(value: str) -> str:
    """SHA-256 hash for PII fields (required by both Facebook and Google)."""
    if not value:
        return ""
    return hashlib.sha256(value.strip().lower().encode("utf-8")).hexdigest()


def _normalize_phone(phone: str) -> str:
    """Normalize Israeli phone to E.164 for hashing."""
    if not phone:
        return ""
    digits = "".join(c for c in phone if c.isdigit())
    if digits.startswith("972"):
        return f"+{digits}"
    if digits.startswith("0"):
        return f"+972{digits[1:]}"
    return f"+972{digits}"


class ConversionTrackingService:
    """Sends server-side conversion events to Facebook CAPI and Google Ads."""

    # Facebook CAPI event names mapped to our internal status
    FB_EVENT_MAP = {
        "lead": "Lead",
        "consultation_booked": "Schedule",
        "converted": "Purchase",
    }

    def send_lead_event(
        self,
        lead_data: Dict[str, Any],
        source_url: str = "",
        event_id: str = "",
    ) -> Dict[str, Any]:
        """Fire a Lead conversion event to all configured ad networks."""
        results = {}

        if Config.is_facebook_pixel_configured() and Config.FACEBOOK_ACCESS_TOKEN:
            results["facebook"] = self._send_fb_event(
                event_name="Lead",
                lead_data=lead_data,
                source_url=source_url,
                event_id=event_id,
            )

        if Config.is_google_conversion_configured():
            results["google"] = self._send_google_conversion(
                conversion_action="lead",
                lead_data=lead_data,
            )

        if not results:
            results["status"] = "no_tracking_configured"

        return results

    def send_status_event(
        self,
        status: str,
        lead_data: Dict[str, Any],
        source_url: str = "",
    ) -> Dict[str, Any]:
        """Fire a conversion event when lead status changes to a conversion milestone."""
        fb_event = self.FB_EVENT_MAP.get(status)
        if not fb_event:
            return {"status": "not_a_conversion_status"}

        results = {}

        if Config.is_facebook_pixel_configured() and Config.FACEBOOK_ACCESS_TOKEN:
            results["facebook"] = self._send_fb_event(
                event_name=fb_event,
                lead_data=lead_data,
                source_url=source_url,
            )

        if Config.is_google_conversion_configured() and status in ("consultation_booked", "converted"):
            results["google"] = self._send_google_conversion(
                conversion_action=status,
                lead_data=lead_data,
            )

        return results

    # ------------------------------------------------------------------
    # Facebook Conversions API
    # ------------------------------------------------------------------

    def _send_fb_event(
        self,
        event_name: str,
        lead_data: Dict[str, Any],
        source_url: str = "",
        event_id: str = "",
    ) -> Dict[str, Any]:
        """Send a single event to Facebook Conversions API."""
        pixel_id = Config.FACEBOOK_PIXEL_ID
        access_token = Config.FACEBOOK_ACCESS_TOKEN

        if not pixel_id or not access_token:
            return {"success": False, "error": "Facebook pixel or token not configured"}

        user_data = {}
        if lead_data.get("email"):
            user_data["em"] = [_hash_value(lead_data["email"])]
        if lead_data.get("phone"):
            user_data["ph"] = [_hash_value(_normalize_phone(lead_data["phone"]))]
        if lead_data.get("name"):
            parts = lead_data["name"].strip().split()
            if parts:
                user_data["fn"] = [_hash_value(parts[0])]
            if len(parts) > 1:
                user_data["ln"] = [_hash_value(parts[-1])]
        user_data["country"] = [_hash_value("il")]

        event = {
            "event_name": event_name,
            "event_time": int(time.time()),
            "action_source": "website",
            "user_data": user_data,
        }

        if source_url:
            event["event_source_url"] = source_url
        if event_id:
            event["event_id"] = event_id

        payload = {"data": [event], "access_token": access_token}

        try:
            url = f"https://graph.facebook.com/v19.0/{pixel_id}/events"
            resp = requests.post(url, json=payload, timeout=10)
            result = resp.json()

            if resp.status_code == 200:
                logger.info(f"Facebook CAPI: {event_name} event sent successfully")
                return {"success": True, "events_received": result.get("events_received", 0)}
            else:
                logger.warning(f"Facebook CAPI error: {result}")
                return {"success": False, "error": result.get("error", {}).get("message", str(result))}
        except Exception as e:
            logger.error(f"Facebook CAPI request failed: {e}")
            return {"success": False, "error": str(e)}

    # ------------------------------------------------------------------
    # Google Ads Enhanced Conversions
    # ------------------------------------------------------------------

    def _send_google_conversion(
        self,
        conversion_action: str,
        lead_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Record a Google Ads offline conversion.
        In production, this uses the Google Ads API to upload offline conversions.
        For now, we log the event for later batch upload or manual import.
        """
        conversion_id = Config.GOOGLE_ADS_CONVERSION_ID
        conversion_label = Config.GOOGLE_ADS_CONVERSION_LABEL

        if not conversion_id:
            return {"success": False, "error": "Google conversion ID not configured"}

        conversion_record = {
            "conversion_action": conversion_action,
            "conversion_id": conversion_id,
            "conversion_label": conversion_label,
            "timestamp": int(time.time()),
            "email_hash": _hash_value(lead_data.get("email", "")),
            "phone_hash": _hash_value(_normalize_phone(lead_data.get("phone", ""))),
            "gclid": lead_data.get("gclid", ""),
        }

        try:
            if Config.is_google_ads_configured():
                self._upload_google_conversion(conversion_record)
                logger.info(f"Google Ads: {conversion_action} conversion uploaded")
                return {"success": True, "method": "api"}
            else:
                logger.info(f"Google Ads: {conversion_action} conversion logged (API not configured)")
                return {"success": True, "method": "logged", "record": conversion_record}
        except Exception as e:
            logger.error(f"Google Ads conversion upload failed: {e}")
            return {"success": False, "error": str(e)}

    def _upload_google_conversion(self, record: dict) -> None:
        """Upload conversion via Google Ads API when fully configured."""
        try:
            from google.ads.googleads.client import GoogleAdsClient

            client = GoogleAdsClient.load_from_dict({
                "developer_token": Config.GOOGLE_ADS_DEVELOPER_TOKEN,
                "client_id": Config.GOOGLE_ADS_CLIENT_ID,
                "client_secret": Config.GOOGLE_ADS_CLIENT_SECRET,
                "refresh_token": Config.GOOGLE_ADS_REFRESH_TOKEN,
                "login_customer_id": Config.GOOGLE_ADS_CUSTOMER_ID,
            })

            service = client.get_service("ConversionUploadService")
            conversion = client.get_type("ClickConversion")
            conversion.conversion_action = (
                f"customers/{Config.GOOGLE_ADS_CUSTOMER_ID}/conversionActions/{record['conversion_id']}"
            )
            conversion.conversion_date_time = time.strftime(
                "%Y-%m-%d %H:%M:%S+02:00", time.localtime(record["timestamp"])
            )

            if record.get("gclid"):
                conversion.gclid = record["gclid"]

            request = client.get_type("UploadClickConversionsRequest")
            request.customer_id = Config.GOOGLE_ADS_CUSTOMER_ID
            request.conversions.append(conversion)
            request.partial_failure = True

            service.upload_click_conversions(request=request)
        except ImportError:
            logger.warning("google-ads package not installed; conversion logged but not uploaded")
        except Exception as e:
            logger.error(f"Google Ads API upload error: {e}")
            raise


# Singleton
conversion_tracker = ConversionTrackingService()
