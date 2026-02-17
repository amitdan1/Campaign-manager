"""
Google Ads API service.
Pulls campaign performance metrics.
Falls back to returning empty data when not configured.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict

from config import Config
from services.circuit_breaker import get_breaker

logger = logging.getLogger("services.google_ads")


class GoogleAdsService:
    """Pull campaign data from Google Ads API."""

    def __init__(self):
        self.configured = Config.is_google_ads_configured()
        self.client = None

        if self.configured:
            try:
                from google.ads.googleads.client import GoogleAdsClient
                self.client = GoogleAdsClient.load_from_dict({
                    "developer_token": Config.GOOGLE_ADS_DEVELOPER_TOKEN,
                    "client_id": Config.GOOGLE_ADS_CLIENT_ID,
                    "client_secret": Config.GOOGLE_ADS_CLIENT_SECRET,
                    "refresh_token": Config.GOOGLE_ADS_REFRESH_TOKEN,
                    "login_customer_id": Config.GOOGLE_ADS_CUSTOMER_ID,
                })
                logger.info("Google Ads API configured")
            except ImportError:
                logger.warning("google-ads package not installed. Run: pip install google-ads")
                self.configured = False
            except Exception as e:
                logger.error(f"Failed to initialize Google Ads client: {e}")
                self.configured = False
        else:
            logger.info("Google Ads not configured. Campaign data will not be pulled.")

    def get_campaign_metrics(self, days: int = 30) -> List[Dict]:
        """
        Pull campaign performance metrics for the last N days.
        Returns list of dicts with campaign data.
        """
        if not self.configured or not self.client:
            logger.info("[DRY RUN] Google Ads metrics requested but not configured")
            return []

        breaker = get_breaker("google_ads")
        if not breaker.is_closed():
            logger.warning("Google Ads circuit breaker OPEN -- skipping metrics pull")
            return []

        try:
            ga_service = self.client.get_service("GoogleAdsService")
            customer_id = Config.GOOGLE_ADS_CUSTOMER_ID

            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            end_date = datetime.now().strftime("%Y-%m-%d")

            query = f"""
                SELECT
                    campaign.id,
                    campaign.name,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.conversions,
                    metrics.cost_micros,
                    metrics.ctr,
                    metrics.average_cpc,
                    segments.date
                FROM campaign
                WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
                    AND campaign.status = 'ENABLED'
                ORDER BY segments.date DESC
            """

            results = ga_service.search(customer_id=customer_id, query=query)

            campaigns = []
            for row in results:
                campaigns.append({
                    "campaign_id": str(row.campaign.id),
                    "campaign_name": row.campaign.name,
                    "platform": "google",
                    "date": row.segments.date,
                    "impressions": row.metrics.impressions,
                    "clicks": row.metrics.clicks,
                    "conversions": int(row.metrics.conversions),
                    "cost": row.metrics.cost_micros / 1_000_000,  # Convert micros to currency
                    "ctr": row.metrics.ctr * 100,
                })
            breaker.record_success()
            return campaigns

        except Exception as e:
            breaker.record_failure()
            logger.error(f"Error fetching Google Ads metrics: {e}")
            return []

    def is_available(self) -> bool:
        return self.configured
