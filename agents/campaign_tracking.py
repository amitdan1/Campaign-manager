"""
Campaign Tracking Agent (pure automation).
Pulls metrics from Google Ads and Facebook APIs,
stores them in the database, and detects anomalies.
"""

from datetime import datetime
from typing import Any, Dict, List

from agents.base_agent import BaseAgent
from models.campaign import Campaign
from services.database import get_session
from services.google_ads_service import GoogleAdsService
from services.facebook_service import FacebookService


class CampaignTrackingAgent(BaseAgent):
    """Tracks campaign performance across all ad platforms."""

    def __init__(self):
        super().__init__(name="CampaignTracking")
        self.google_ads = GoogleAdsService()
        self.facebook = FacebookService()

    def run(self, days: int = 30, **kwargs) -> Dict[str, Any]:
        """
        Pull latest campaign metrics from all platforms and store them.
        Also checks for anomalies and records performance in agent memory
        for closed-loop content optimization.
        """
        results = {
            "google": self._pull_google_metrics(days),
            "facebook": self._pull_facebook_metrics(days),
        }

        # Detect anomalies across all stored campaigns
        anomalies = self._detect_anomalies()

        # Record performance in agent memory for Content/LandingPage agents
        self._record_performance_memories(days)

        total_synced = sum(r.get("synced", 0) for r in results.values())
        return {
            "success": True,
            "total_synced": total_synced,
            "platforms": results,
            "anomalies": anomalies,
        }

    def _pull_google_metrics(self, days: int) -> dict:
        """Pull and store Google Ads metrics."""
        if not self.google_ads.is_available():
            return {"available": False, "synced": 0, "message": "Google Ads not configured"}

        try:
            metrics = self.google_ads.get_campaign_metrics(days=days)
            stored = self._store_metrics(metrics)
            self.logger.info(f"Google Ads: synced {stored} campaign records")
            return {"available": True, "synced": stored}
        except Exception as e:
            self.logger.error(f"Error pulling Google Ads metrics: {e}")
            return {"available": True, "synced": 0, "error": str(e)}

    def _pull_facebook_metrics(self, days: int) -> dict:
        """Pull and store Facebook metrics."""
        if not self.facebook.is_available():
            return {"available": False, "synced": 0, "message": "Facebook API not configured"}

        try:
            metrics = self.facebook.get_campaign_metrics(days=days)
            stored = self._store_metrics(metrics)
            self.logger.info(f"Facebook: synced {stored} campaign records")
            return {"available": True, "synced": stored}
        except Exception as e:
            self.logger.error(f"Error pulling Facebook metrics: {e}")
            return {"available": True, "synced": 0, "error": str(e)}

    def _store_metrics(self, metrics: List[dict]) -> int:
        """Store a list of campaign metric dicts in the database."""
        if not metrics:
            return 0

        session = get_session()
        stored = 0
        try:
            for m in metrics:
                impressions = m.get("impressions", 0)
                clicks = m.get("clicks", 0)
                conversions = m.get("conversions", 0)
                cost = m.get("cost", 0)

                ctr = (clicks / impressions * 100) if impressions > 0 else 0
                conversion_rate = (conversions / clicks * 100) if clicks > 0 else 0
                cpl = (cost / conversions) if conversions > 0 else 0

                campaign = Campaign(
                    campaign_id=m.get("campaign_id", ""),
                    campaign_name=m.get("campaign_name", ""),
                    platform=m.get("platform", ""),
                    date=datetime.fromisoformat(m["date"]) if isinstance(m.get("date"), str) and m.get("date") else datetime.utcnow(),
                    impressions=impressions,
                    clicks=clicks,
                    conversions=conversions,
                    cost=cost,
                    cpl=cpl,
                    ctr=ctr,
                    conversion_rate=conversion_rate,
                )
                session.add(campaign)
                stored += 1

            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error storing metrics: {e}")
        finally:
            session.close()

        return stored

    def _detect_anomalies(self) -> List[dict]:
        """
        Detect anomalies in recent campaign data:
        - CPL spike (>50% above target)
        - Budget exhaustion (cost > 90% of monthly budget)
        - Zero conversions with significant spend
        """
        anomalies = []
        target_cpl = self.config.TARGET_CPL
        monthly_budget = self.config.BUDGET_TOTAL

        session = get_session()
        try:
            # Get last 30 days of data grouped by campaign
            from sqlalchemy import func
            from datetime import timedelta

            cutoff = datetime.utcnow() - timedelta(days=30)

            campaign_stats = (
                session.query(
                    Campaign.campaign_name,
                    Campaign.platform,
                    func.sum(Campaign.cost).label("total_cost"),
                    func.sum(Campaign.conversions).label("total_conversions"),
                    func.sum(Campaign.clicks).label("total_clicks"),
                )
                .filter(Campaign.date >= cutoff)
                .group_by(Campaign.campaign_name, Campaign.platform)
                .all()
            )

            total_spend = 0
            for stat in campaign_stats:
                name, platform, cost, conversions, clicks = stat
                total_spend += (cost or 0)
                cpl = (cost / conversions) if conversions and conversions > 0 else 0

                # High CPL
                if cpl > target_cpl * 1.5 and conversions > 0:
                    anomalies.append({
                        "type": "high_cpl",
                        "campaign": name,
                        "platform": platform,
                        "value": round(cpl, 2),
                        "threshold": target_cpl * 1.5,
                        "severity": "high",
                        "message": f"CPL ₪{cpl:.0f} is >50% above target ₪{target_cpl}",
                    })

                # Zero conversions with spend
                if (cost or 0) > 50 and (conversions or 0) == 0:
                    anomalies.append({
                        "type": "zero_conversions",
                        "campaign": name,
                        "platform": platform,
                        "value": cost,
                        "severity": "high",
                        "message": f"₪{cost:.0f} spent with zero conversions",
                    })

            # Budget exhaustion check
            if total_spend > monthly_budget * 0.9:
                anomalies.append({
                    "type": "budget_exhaustion",
                    "campaign": "All campaigns",
                    "platform": "all",
                    "value": round(total_spend, 2),
                    "threshold": monthly_budget,
                    "severity": "medium",
                    "message": f"Total spend ₪{total_spend:.0f} is >90% of ₪{monthly_budget} monthly budget",
                })

        except Exception as e:
            self.logger.error(f"Error detecting anomalies: {e}")
        finally:
            session.close()

        return anomalies

    def get_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get a summary of campaign performance."""
        session = get_session()
        try:
            from datetime import timedelta
            cutoff = datetime.utcnow() - timedelta(days=days)

            campaigns = session.query(Campaign).filter(Campaign.date >= cutoff).all()

            if not campaigns:
                return {"success": True, "message": "No campaign data yet", "data": {}}

            total_cost = sum(c.cost for c in campaigns)
            total_clicks = sum(c.clicks for c in campaigns)
            total_impressions = sum(c.impressions for c in campaigns)
            total_conversions = sum(c.conversions for c in campaigns)

            return {
                "success": True,
                "data": {
                    "total_campaigns": len(set(c.campaign_name for c in campaigns)),
                    "total_cost": round(total_cost, 2),
                    "total_clicks": total_clicks,
                    "total_impressions": total_impressions,
                    "total_conversions": total_conversions,
                    "avg_cpl": round(total_cost / total_conversions, 2) if total_conversions > 0 else 0,
                    "avg_ctr": round(total_clicks / total_impressions * 100, 2) if total_impressions > 0 else 0,
                    "avg_conversion_rate": round(total_conversions / total_clicks * 100, 2) if total_clicks > 0 else 0,
                },
            }
        finally:
            session.close()

    def _record_performance_memories(self, days: int) -> None:
        """
        Store campaign performance data in agent memory so Content and
        LandingPage agents can learn from real results (closed-loop optimization).
        """
        from services.agent_memory import memory_service
        from sqlalchemy import func

        session = get_session()
        try:
            from datetime import timedelta
            cutoff = datetime.utcnow() - timedelta(days=days)

            campaign_stats = (
                session.query(
                    Campaign.campaign_name,
                    Campaign.platform,
                    func.sum(Campaign.cost).label("total_cost"),
                    func.sum(Campaign.conversions).label("total_conversions"),
                    func.sum(Campaign.clicks).label("total_clicks"),
                    func.sum(Campaign.impressions).label("total_impressions"),
                )
                .filter(Campaign.date >= cutoff)
                .group_by(Campaign.campaign_name, Campaign.platform)
                .all()
            )

            for stat in campaign_stats:
                name, platform, cost, conversions, clicks, impressions = stat
                cost = cost or 0
                clicks = clicks or 0
                impressions = impressions or 0
                conversions = conversions or 0

                metrics = {
                    "impressions": impressions,
                    "clicks": clicks,
                    "conversions": conversions,
                    "cost": round(float(cost), 2),
                    "ctr": round(clicks / impressions * 100, 2) if impressions > 0 else 0,
                    "cpl": round(float(cost) / conversions, 2) if conversions > 0 else 0,
                    "conversion_rate": round(conversions / clicks * 100, 2) if clicks > 0 else 0,
                }

                for agent in ("Content", "LandingPage"):
                    memory_service.record_campaign_performance(
                        agent_name=agent,
                        campaign_name=name,
                        platform=platform,
                        metrics=metrics,
                    )

            self.logger.info(f"Recorded performance memories for {len(campaign_stats)} campaigns")
        except Exception as e:
            self.logger.error(f"Error recording performance memories: {e}")
        finally:
            session.close()

    def health_check(self) -> Dict[str, Any]:
        return {
            "healthy": True,
            "google_ads_configured": self.google_ads.is_available(),
            "facebook_configured": self.facebook.is_available(),
        }
