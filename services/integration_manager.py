"""
Integration Manager — registry of all external integrations,
.env read/write, connection testing, and status reporting.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import dotenv_values, set_key

from config import Config

logger = logging.getLogger("services.integration_manager")

# Path to the project-level .env file
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"

# ---------------------------------------------------------------------------
# Integration registry — single source of truth for every integration
# ---------------------------------------------------------------------------
# Each field dict:
#   key      — env var name
#   label    — Hebrew UI label
#   secret   — True ⇒ mask the value in the API response
#   required — True ⇒ must be set for the integration to be "connected"

INTEGRATIONS: List[Dict[str, Any]] = [
    {
        "id": "openai",
        "name": "OpenAI",
        "icon": "fa-brain",
        "description": "יצירת תוכן, ניקוד לידים ותכנון אסטרטגי באמצעות AI",
        "config_check": "is_openai_configured",
        "fields": [
            {"key": "OPENAI_API_KEY", "label": "API Key", "secret": True, "required": True},
            {"key": "OPENAI_MODEL", "label": "מודל", "secret": False, "required": False},
        ],
    },
    {
        "id": "meta",
        "name": "Meta / Facebook Ads",
        "icon": "fa-meta",
        "description": "ניהול קמפיינים, מעקב המרות ופיקסל ב-Facebook ו-Instagram",
        "config_check": "is_facebook_configured",
        "fields": [
            {"key": "FACEBOOK_ACCESS_TOKEN", "label": "Access Token", "secret": True, "required": True},
            {"key": "FACEBOOK_AD_ACCOUNT_ID", "label": "Ad Account ID", "secret": False, "required": True},
            {"key": "FACEBOOK_PIXEL_ID", "label": "Pixel ID", "secret": False, "required": False},
        ],
    },
    {
        "id": "google_ads",
        "name": "Google Ads",
        "icon": "fa-google",
        "description": "ניהול קמפיינים, מעקב ביצועים ומעקב המרות ב-Google Ads",
        "config_check": "is_google_ads_configured",
        "fields": [
            {"key": "GOOGLE_ADS_DEVELOPER_TOKEN", "label": "Developer Token", "secret": True, "required": True},
            {"key": "GOOGLE_ADS_CLIENT_ID", "label": "Client ID", "secret": False, "required": False},
            {"key": "GOOGLE_ADS_CLIENT_SECRET", "label": "Client Secret", "secret": True, "required": False},
            {"key": "GOOGLE_ADS_REFRESH_TOKEN", "label": "Refresh Token", "secret": True, "required": False},
            {"key": "GOOGLE_ADS_CUSTOMER_ID", "label": "Customer ID", "secret": False, "required": True},
            {"key": "GOOGLE_ADS_CONVERSION_ID", "label": "Conversion ID (מעקב המרות)", "secret": False, "required": False},
            {"key": "GOOGLE_ADS_CONVERSION_LABEL", "label": "Conversion Label", "secret": False, "required": False},
        ],
    },
    {
        "id": "sendgrid",
        "name": "SendGrid (Email)",
        "icon": "fa-envelope",
        "description": "שליחת מיילים אוטומטית ללידים ולקוחות",
        "config_check": "is_email_configured",
        "fields": [
            {"key": "SENDGRID_API_KEY", "label": "API Key", "secret": True, "required": True},
            {"key": "SENDGRID_FROM_EMAIL", "label": "כתובת שולח", "secret": False, "required": False},
        ],
    },
    {
        "id": "twilio",
        "name": "Twilio (WhatsApp)",
        "icon": "fa-whatsapp",
        "description": "שליחת הודעות WhatsApp אוטומטיות ללידים",
        "config_check": "is_whatsapp_configured",
        "fields": [
            {"key": "TWILIO_ACCOUNT_SID", "label": "Account SID", "secret": True, "required": True},
            {"key": "TWILIO_AUTH_TOKEN", "label": "Auth Token", "secret": True, "required": True},
            {"key": "TWILIO_WHATSAPP_FROM", "label": "מספר WhatsApp", "secret": False, "required": False},
        ],
    },
]

# Whitelist of env var keys that the UI is allowed to write
_ALLOWED_KEYS = {f["key"] for integ in INTEGRATIONS for f in integ["fields"]}


def _mask_value(value: str) -> str:
    """Mask a secret value, showing first 4 and last 3 characters."""
    if not value or len(value) <= 8:
        return "••••••••" if value else ""
    return value[:4] + "•" * (len(value) - 7) + value[-3:]


def _ensure_env_file() -> Path:
    """Create .env from .env.example if it doesn't exist."""
    if not _ENV_PATH.exists():
        example = _ENV_PATH.parent / ".env.example"
        if example.exists():
            import shutil
            shutil.copy(example, _ENV_PATH)
            logger.info("Created .env from .env.example")
        else:
            _ENV_PATH.touch()
            logger.info("Created empty .env file")
    return _ENV_PATH


def _reload_config_attr(key: str) -> None:
    """
    Reload a single Config class attribute from the current environment.
    We re-read os.environ because set_key already writes to both the file
    and os.environ when called with the override flag.
    """
    val = os.environ.get(key, "")
    if hasattr(Config, key):
        setattr(Config, key, val)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class IntegrationManager:
    """Central manager for all external integrations."""

    def get_all_statuses(self) -> List[Dict[str, Any]]:
        """Return status and (masked) field values for every integration."""
        env_path = _ensure_env_file()
        env_values = dotenv_values(env_path)

        result = []
        for integ in INTEGRATIONS:
            # Check connection via Config helper
            checker = getattr(Config, integ["config_check"], None)
            connected = checker() if callable(checker) else False

            fields = []
            for f in integ["fields"]:
                raw = env_values.get(f["key"], "") or ""
                entry: Dict[str, Any] = {
                    "key": f["key"],
                    "label": f["label"],
                    "secret": f["secret"],
                    "required": f.get("required", False),
                    "has_value": bool(raw),
                }
                if f["secret"]:
                    entry["masked"] = _mask_value(raw)
                else:
                    entry["value"] = raw
                fields.append(entry)

            result.append({
                "id": integ["id"],
                "name": integ["name"],
                "icon": integ["icon"],
                "description": integ["description"],
                "connected": connected,
                "fields": fields,
            })
        return result

    def save_keys(self, integration_id: str, fields: Dict[str, str]) -> Dict[str, Any]:
        """
        Write the supplied key-value pairs into .env and reload Config.
        Returns {"success": True} or {"success": False, "error": "..."}.
        """
        # Validate integration exists
        integ = next((i for i in INTEGRATIONS if i["id"] == integration_id), None)
        if not integ:
            return {"success": False, "error": f"Unknown integration: {integration_id}"}

        # Validate all keys belong to this integration's whitelist
        valid_keys = {f["key"] for f in integ["fields"]}
        for k in fields:
            if k not in valid_keys:
                return {"success": False, "error": f"Key '{k}' is not valid for {integ['name']}"}
            if k not in _ALLOWED_KEYS:
                return {"success": False, "error": f"Key '{k}' is not an allowed env variable"}

        env_path = _ensure_env_file()

        try:
            for k, v in fields.items():
                # set_key writes to the file AND updates os.environ
                set_key(str(env_path), k, v)
                _reload_config_attr(k)
            logger.info(f"Saved {len(fields)} keys for integration '{integration_id}'")
            return {"success": True}
        except Exception as e:
            logger.error(f"Error saving keys for {integration_id}: {e}")
            return {"success": False, "error": str(e)}

    def test_connection(self, integration_id: str) -> Dict[str, Any]:
        """
        Run a lightweight connection test for the given integration.
        Returns {"success": True/False, "message": "..."}.
        """
        tester = _TESTERS.get(integration_id)
        if not tester:
            return {"success": False, "message": f"No tester for integration: {integration_id}"}
        try:
            return tester()
        except Exception as e:
            logger.error(f"Connection test failed for {integration_id}: {e}")
            return {"success": False, "message": str(e)}


# ---------------------------------------------------------------------------
# Connection testers (one per integration)
# ---------------------------------------------------------------------------

def _test_openai() -> Dict[str, Any]:
    if not Config.is_openai_configured():
        return {"success": False, "message": "מפתח API לא מוגדר"}
    try:
        from openai import OpenAI
        client = OpenAI(api_key=Config.OPENAI_API_KEY)
        models = client.models.list()
        # Just check we got a response
        count = sum(1 for _ in models)
        return {"success": True, "message": f"מחובר בהצלחה ({count} מודלים זמינים)"}
    except Exception as e:
        return {"success": False, "message": f"שגיאת חיבור: {e}"}


def _test_meta() -> Dict[str, Any]:
    if not Config.is_facebook_configured():
        return {"success": False, "message": "Access Token או Ad Account ID לא מוגדרים"}
    try:
        from facebook_business.api import FacebookAdsApi
        from facebook_business.adobjects.adaccount import AdAccount
        FacebookAdsApi.init(access_token=Config.FACEBOOK_ACCESS_TOKEN)
        account = AdAccount(f"act_{Config.FACEBOOK_AD_ACCOUNT_ID}")
        info = account.api_get(fields=["name", "account_status"])
        return {"success": True, "message": f"מחובר לחשבון: {info.get('name', Config.FACEBOOK_AD_ACCOUNT_ID)}"}
    except ImportError:
        return {"success": False, "message": "חבילת facebook-business לא מותקנת. הרץ: pip install facebook-business"}
    except Exception as e:
        return {"success": False, "message": f"שגיאת חיבור: {e}"}


def _test_google_ads() -> Dict[str, Any]:
    if not Config.is_google_ads_configured():
        return {"success": False, "message": "Developer Token או Customer ID לא מוגדרים"}
    try:
        from google.ads.googleads.client import GoogleAdsClient
        client = GoogleAdsClient.load_from_dict({
            "developer_token": Config.GOOGLE_ADS_DEVELOPER_TOKEN,
            "client_id": Config.GOOGLE_ADS_CLIENT_ID,
            "client_secret": Config.GOOGLE_ADS_CLIENT_SECRET,
            "refresh_token": Config.GOOGLE_ADS_REFRESH_TOKEN,
            "login_customer_id": Config.GOOGLE_ADS_CUSTOMER_ID,
        })
        customer_service = client.get_service("CustomerService")
        accessible = customer_service.list_accessible_customers()
        count = len(accessible.resource_names)
        return {"success": True, "message": f"מחובר בהצלחה ({count} חשבונות נגישים)"}
    except ImportError:
        return {"success": False, "message": "חבילת google-ads לא מותקנת. הרץ: pip install google-ads"}
    except Exception as e:
        return {"success": False, "message": f"שגיאת חיבור: {e}"}


def _test_sendgrid() -> Dict[str, Any]:
    if not Config.is_email_configured():
        return {"success": False, "message": "מפתח API לא מוגדר"}
    try:
        import sendgrid
        sg = sendgrid.SendGridAPIClient(api_key=Config.SENDGRID_API_KEY)
        response = sg.client.user.profile.get()
        if response.status_code == 200:
            return {"success": True, "message": "מחובר בהצלחה ל-SendGrid"}
        return {"success": False, "message": f"תגובת SendGrid: {response.status_code}"}
    except ImportError:
        return {"success": False, "message": "חבילת sendgrid לא מותקנת. הרץ: pip install sendgrid"}
    except Exception as e:
        return {"success": False, "message": f"שגיאת חיבור: {e}"}


def _test_twilio() -> Dict[str, Any]:
    if not Config.is_whatsapp_configured():
        return {"success": False, "message": "Account SID או Auth Token לא מוגדרים"}
    try:
        from twilio.rest import Client
        client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
        account = client.api.accounts(Config.TWILIO_ACCOUNT_SID).fetch()
        return {"success": True, "message": f"מחובר לחשבון: {account.friendly_name}"}
    except ImportError:
        return {"success": False, "message": "חבילת twilio לא מותקנת. הרץ: pip install twilio"}
    except Exception as e:
        return {"success": False, "message": f"שגיאת חיבור: {e}"}


_TESTERS = {
    "openai": _test_openai,
    "meta": _test_meta,
    "google_ads": _test_google_ads,
    "sendgrid": _test_sendgrid,
    "twilio": _test_twilio,
}
