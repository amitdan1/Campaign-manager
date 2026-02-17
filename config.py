"""
Centralized configuration loaded from environment variables.
Uses .env file for local development.
"""

import os
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()


class Config:
    """Application configuration from environment variables."""

    # --- Business Info ---
    BUSINESS_NAME = os.getenv("BUSINESS_NAME", "Ofir Assulin Interior Design")
    BUSINESS_PHONE = os.getenv("BUSINESS_PHONE", "052-626-9261")
    BUSINESS_EMAIL = os.getenv("BUSINESS_EMAIL", "ofirassulin.design@gmail.com")
    BUSINESS_WEBSITE = os.getenv("BUSINESS_WEBSITE", "https://www.ofirassulin.design/")

    # --- Budget (NIS/month) ---
    BUDGET_TOTAL = int(os.getenv("BUDGET_TOTAL", "500"))
    BUDGET_GOOGLE_ADS = int(os.getenv("BUDGET_GOOGLE_ADS", "300"))
    BUDGET_FACEBOOK = int(os.getenv("BUDGET_FACEBOOK", "200"))

    # --- KPI Targets ---
    TARGET_CPL = int(os.getenv("TARGET_CPL", "200"))
    TARGET_CONSULTATION_RATE = float(os.getenv("TARGET_CONSULTATION_RATE", "0.40"))
    TARGET_CONVERSION_RATE = float(os.getenv("TARGET_CONVERSION_RATE", "0.50"))
    TARGET_CAC = int(os.getenv("TARGET_CAC", "300"))
    TARGET_ROAS = int(os.getenv("TARGET_ROAS", "200"))

    # --- Target Audience ---
    TARGET_AGE_MIN = int(os.getenv("TARGET_AGE_MIN", "35"))
    TARGET_AGE_MAX = int(os.getenv("TARGET_AGE_MAX", "55"))
    TARGET_LOCATIONS = os.getenv(
        "TARGET_LOCATIONS", "תל אביב,הרצליה,רמת השרון,כפר שמריהו,סביון"
    ).split(",")
    TARGET_MIN_PROJECT_BUDGET = int(os.getenv("TARGET_MIN_PROJECT_BUDGET", "500000"))

    # --- Database ---
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///marketing.db")

    # --- OpenAI ---
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    DAILY_TOKEN_LIMIT = int(os.getenv("DAILY_TOKEN_LIMIT", "500000"))

    # --- SendGrid (Email) ---
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
    SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", BUSINESS_EMAIL)

    # --- Twilio (WhatsApp) ---
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM", "")

    # --- Google Ads ---
    GOOGLE_ADS_DEVELOPER_TOKEN = os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN", "")
    GOOGLE_ADS_CLIENT_ID = os.getenv("GOOGLE_ADS_CLIENT_ID", "")
    GOOGLE_ADS_CLIENT_SECRET = os.getenv("GOOGLE_ADS_CLIENT_SECRET", "")
    GOOGLE_ADS_REFRESH_TOKEN = os.getenv("GOOGLE_ADS_REFRESH_TOKEN", "")
    GOOGLE_ADS_CUSTOMER_ID = os.getenv("GOOGLE_ADS_CUSTOMER_ID", "")

    # --- Facebook Marketing API ---
    FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN", "")
    FACEBOOK_AD_ACCOUNT_ID = os.getenv("FACEBOOK_AD_ACCOUNT_ID", "")
    FACEBOOK_PIXEL_ID = os.getenv("FACEBOOK_PIXEL_ID", "")

    # --- Google Ads Conversion Tracking ---
    GOOGLE_ADS_CONVERSION_ID = os.getenv("GOOGLE_ADS_CONVERSION_ID", "")
    GOOGLE_ADS_CONVERSION_LABEL = os.getenv("GOOGLE_ADS_CONVERSION_LABEL", "")

    # --- Service Segments ---
    SERVICE_SEGMENTS = [
        {
            "id": "villa_new_build",
            "name": "בוני וילות חדשות",
            "name_en": "New Villa Builders",
            "pain_points": ["מוצפים מהחלטות עיצוב", "פחד מטעויות יקרות", "צריכים ליווי מקצועי מא' ועד ת'"],
            "key_message": "בונים בית חדש? נלווה אתכם מהתכנון ועד ההלבשה — בדיוק כמו שדמיינתם",
            "keywords": ["עיצוב פנים וילה", "מעצבת פנים בתים פרטיים", "עיצוב פנים בית חדש"],
            "project_types": ["villa", "new_build"],
        },
        {
            "id": "renovation",
            "name": "משפצים",
            "name_en": "Renovators",
            "pain_points": ["לא יודעים מאיפה להתחיל", "חוששים מחריגות תקציב", "רוצים שמישהו ינהל הכל"],
            "key_message": "שיפוץ לא חייב להיות כאב ראש — ליווי מקצועי שמבטיח שקט נפשי ותוצאה מושלמת",
            "keywords": ["שיפוץ דירה יוקרתית", "מעצבת פנים שיפוצים", "שיפוץ מקיף"],
            "project_types": ["renovation"],
        },
        {
            "id": "luxury_apartment",
            "name": "דירות יוקרה ופנטהאוזים",
            "name_en": "Luxury Apartments",
            "pain_points": ["רוצים עיצוב שמרגיש ייחודי ולא 'עוד דירה'", "חשוב להם סטטוס ואסתטיקה", "מחפשים מעצבת עם טעם מוכח"],
            "key_message": "עיצוב פנים שמשקף את מי שאתם — יוקרה שקטה, פרטים מדויקים, תחושת בית",
            "keywords": ["עיצוב פנטהאוז", "עיצוב דירת יוקרה", "מעצבת פנים תל אביב"],
            "project_types": ["penthouse", "luxury_apt"],
        },
    ]

    # --- Flask ---
    FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "change-me-in-production")
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "true").lower() == "true"
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5000").split(",")
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", str(2 * 1024 * 1024)))  # 2MB

    # --- Automation Settings ---
    AUTO_FOLLOWUP = os.getenv("AUTO_FOLLOWUP", "true").lower() == "true"
    FOLLOWUP_DELAY_HOURS = int(os.getenv("FOLLOWUP_DELAY_HOURS", "2"))
    LEAD_SCORING_ENABLED = os.getenv("LEAD_SCORING_ENABLED", "true").lower() == "true"

    @classmethod
    def is_openai_configured(cls) -> bool:
        return bool(cls.OPENAI_API_KEY)

    @classmethod
    def is_email_configured(cls) -> bool:
        return bool(cls.SENDGRID_API_KEY)

    @classmethod
    def is_whatsapp_configured(cls) -> bool:
        return bool(cls.TWILIO_ACCOUNT_SID and cls.TWILIO_AUTH_TOKEN)

    @classmethod
    def is_google_ads_configured(cls) -> bool:
        return bool(cls.GOOGLE_ADS_DEVELOPER_TOKEN and cls.GOOGLE_ADS_CUSTOMER_ID)

    @classmethod
    def is_facebook_configured(cls) -> bool:
        return bool(cls.FACEBOOK_ACCESS_TOKEN and cls.FACEBOOK_AD_ACCOUNT_ID)

    @classmethod
    def is_facebook_pixel_configured(cls) -> bool:
        return bool(cls.FACEBOOK_PIXEL_ID)

    @classmethod
    def is_google_conversion_configured(cls) -> bool:
        return bool(cls.GOOGLE_ADS_CONVERSION_ID)

    @classmethod
    def get_segment_for_project_type(cls, project_type: str) -> dict:
        """Return the matching segment for a project type, or None."""
        if not project_type:
            return None
        for seg in cls.SERVICE_SEGMENTS:
            if project_type in seg["project_types"]:
                return seg
        return None
