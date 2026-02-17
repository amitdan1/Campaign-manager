"""
Facebook Marketing API service.
Pulls campaign performance metrics from Facebook/Instagram Ads.
Falls back to returning empty data when not configured.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict

from config import Config
from services.circuit_breaker import get_breaker

logger = logging.getLogger("services.facebook")


class FacebookService:
    """Pull campaign data from Facebook Marketing API."""

    def __init__(self):
        self.configured = Config.is_facebook_configured()
        self.api = None

        if self.configured:
            try:
                from facebook_business.api import FacebookAdsApi
                from facebook_business.adobjects.adaccount import AdAccount
                FacebookAdsApi.init(access_token=Config.FACEBOOK_ACCESS_TOKEN)
                self.account = AdAccount(f"act_{Config.FACEBOOK_AD_ACCOUNT_ID}")
                logger.info("Facebook Marketing API configured")
            except ImportError:
                logger.warning(
                    "facebook-business package not installed. "
                    "Run: pip install facebook-business"
                )
                self.configured = False
            except Exception as e:
                logger.error(f"Failed to initialize Facebook API: {e}")
                self.configured = False
        else:
            logger.info("Facebook API not configured. Campaign data will not be pulled.")

    def get_campaign_metrics(self, days: int = 30) -> List[Dict]:
        """
        Pull campaign performance metrics for the last N days.
        Returns list of dicts with campaign data.
        """
        if not self.configured:
            logger.info("[DRY RUN] Facebook metrics requested but not configured")
            return []

        breaker = get_breaker("facebook")
        if not breaker.is_closed():
            logger.warning("Facebook circuit breaker OPEN -- skipping metrics pull")
            return []

        try:
            from facebook_business.adobjects.campaign import Campaign

            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            end_date = datetime.now().strftime("%Y-%m-%d")

            campaigns = self.account.get_campaigns(
                fields=[Campaign.Field.name, Campaign.Field.id, Campaign.Field.status],
                params={"effective_status": ["ACTIVE", "PAUSED"]},
            )

            results = []
            for campaign in campaigns:
                insights = campaign.get_insights(
                    fields=[
                        "impressions",
                        "clicks",
                        "actions",
                        "spend",
                        "ctr",
                        "cpc",
                    ],
                    params={
                        "time_range": {"since": start_date, "until": end_date},
                        "time_increment": 1,  # Daily breakdown
                    },
                )

                for insight in insights:
                    # Extract conversions from actions
                    conversions = 0
                    if insight.get("actions"):
                        for action in insight["actions"]:
                            if action["action_type"] in (
                                "lead",
                                "offsite_conversion.fb_pixel_lead",
                            ):
                                conversions += int(action["value"])

                    results.append({
                        "campaign_id": campaign["id"],
                        "campaign_name": campaign["name"],
                        "platform": "facebook",
                        "date": insight.get("date_start", ""),
                        "impressions": int(insight.get("impressions", 0)),
                        "clicks": int(insight.get("clicks", 0)),
                        "conversions": conversions,
                        "cost": float(insight.get("spend", 0)),
                        "ctr": float(insight.get("ctr", 0)),
                    })

            breaker.record_success()
            return results

        except Exception as e:
            breaker.record_failure()
            logger.error(f"Error fetching Facebook metrics: {e}")
            return []

    def is_available(self) -> bool:
        return self.configured
