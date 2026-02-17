"""
Agent Orchestrator - Central coordinator for all marketing agents.
Initializes agents lazily, routes tasks, and provides a unified interface.
"""

import logging
from typing import Any, Dict

from services.database import init_db

logger = logging.getLogger("orchestrator")


class AgentOrchestrator:
    """
    Central coordinator that initializes all agents and provides
    a single entry point for the Flask app and any other callers.
    """

    def __init__(self):
        logger.info("Initializing Agent Orchestrator...")
        init_db()
        logger.info("Database initialized")

        # All agents are lazily loaded to avoid circular imports
        self._agents = {}
        logger.info("Agent Orchestrator ready")

    # --- Lazy agent accessors ---

    def _get(self, key, factory):
        if key not in self._agents:
            self._agents[key] = factory()
        return self._agents[key]

    @property
    def lead_capture(self):
        def factory():
            from agents.lead_capture import LeadCaptureAgent
            return LeadCaptureAgent()
        return self._get("lead_capture", factory)

    @property
    def lead_scoring(self):
        def factory():
            from agents.lead_scoring import LeadScoringAgent
            return LeadScoringAgent()
        return self._get("lead_scoring", factory)

    @property
    def funnel_automation(self):
        def factory():
            from agents.funnel_automation import FunnelAutomationAgent
            return FunnelAutomationAgent()
        return self._get("funnel_automation", factory)

    @property
    def campaign_tracking(self):
        def factory():
            from agents.campaign_tracking import CampaignTrackingAgent
            return CampaignTrackingAgent()
        return self._get("campaign_tracking", factory)

    @property
    def optimization(self):
        def factory():
            from agents.optimization import OptimizationAgent
            return OptimizationAgent()
        return self._get("optimization", factory)

    @property
    def content(self):
        def factory():
            from agents.content import ContentAgent
            return ContentAgent()
        return self._get("content", factory)

    @property
    def brand_scraper(self):
        def factory():
            from agents.brand_scraper import BrandScraperAgent
            return BrandScraperAgent()
        return self._get("brand_scraper", factory)

    @property
    def strategy(self):
        def factory():
            from agents.strategy import StrategyAgent
            return StrategyAgent()
        return self._get("strategy", factory)

    @property
    def landing_page(self):
        def factory():
            from agents.landing_page import LandingPageAgent
            return LandingPageAgent()
        return self._get("landing_page", factory)

    @property
    def campaign_manager(self):
        def factory():
            from agents.campaign_manager import CampaignManagerAgent
            return CampaignManagerAgent()
        return self._get("campaign_manager", factory)

    @property
    def budget_optimizer(self):
        def factory():
            from agents.budget_optimizer import BudgetOptimizerAgent
            return BudgetOptimizerAgent()
        return self._get("budget_optimizer", factory)

    # --- High-level workflows ---

    def capture_and_score_lead(self, **lead_data) -> Dict[str, Any]:
        """Full lead intake: capture -> score -> return combined result."""
        capture_result = self.lead_capture.run(**lead_data)
        if not capture_result.get("success"):
            return capture_result

        lead_id = capture_result["lead_id"]
        score_result = self.lead_scoring.run(lead_id=lead_id)

        return {
            "success": True,
            "lead_id": lead_id,
            "lead": capture_result.get("lead", {}),
            "scoring": {
                "score": score_result.get("score"),
                "reasoning": score_result.get("reasoning"),
                "priority": score_result.get("priority"),
                "recommended_action": score_result.get("recommended_action"),
                "method": score_result.get("method"),
            },
        }

    def get_dashboard_stats(self, days: int = 30) -> Dict[str, Any]:
        """Aggregate stats using SQL queries instead of loading all rows into Python."""
        from datetime import datetime, timedelta
        from sqlalchemy import func
        from services.database import get_session
        from models.lead import Lead
        from models.campaign import Campaign
        from models.proposal import Proposal

        session = get_session()
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)
            cutoff_7d = datetime.utcnow() - timedelta(days=7)
            cutoff_14d = datetime.utcnow() - timedelta(days=14)

            # B4: All counts via SQL aggregate, no full-table loads
            total_leads = session.query(func.count(Lead.id)).filter(Lead.created_at >= cutoff).scalar() or 0
            qualified_leads = session.query(func.count(Lead.id)).filter(Lead.created_at >= cutoff, Lead.quality_score >= 7).scalar() or 0
            consultations = session.query(func.count(Lead.id)).filter(Lead.created_at >= cutoff, Lead.status == "consultation_booked").scalar() or 0
            conversions = session.query(func.count(Lead.id)).filter(Lead.created_at >= cutoff, Lead.status == "converted").scalar() or 0

            # Campaign aggregates
            camp_agg = session.query(
                func.coalesce(func.sum(Campaign.cost), 0),
                func.coalesce(func.sum(Campaign.conversions), 0),
            ).filter(Campaign.date >= cutoff).first()
            total_spend = float(camp_agg[0])
            total_conv = int(camp_agg[1])
            avg_cpl = (total_spend / total_conv) if total_conv > 0 else 0

            consultation_rate = (consultations / total_leads * 100) if total_leads > 0 else 0
            conversion_rate = (conversions / consultations * 100) if consultations > 0 else 0
            cac = (total_spend / conversions) if conversions > 0 else 0

            # Group-by queries
            source_rows = session.query(Lead.source, func.count(Lead.id)).filter(Lead.created_at >= cutoff).group_by(Lead.source).all()
            leads_by_source = {row[0]: row[1] for row in source_rows}

            status_rows = session.query(Lead.status, func.count(Lead.id)).filter(Lead.created_at >= cutoff).group_by(Lead.status).all()
            status_map = {row[0]: row[1] for row in status_rows}
            status_breakdown = {s: status_map.get(s, 0) for s in ["new", "contacted", "qualified", "consultation_booked", "converted", "lost"]}

            # Trend
            last_7_count = session.query(func.count(Lead.id)).filter(Lead.created_at >= cutoff_7d).scalar() or 0
            prev_7_count = session.query(func.count(Lead.id)).filter(Lead.created_at >= cutoff_14d, Lead.created_at < cutoff_7d).scalar() or 0
            trend_pct = ((last_7_count - prev_7_count) / prev_7_count * 100) if prev_7_count else 0

            pending_proposals = session.query(func.count(Proposal.id)).filter(Proposal.status == "pending_review").scalar() or 0

            return {
                "success": True,
                "stats": {
                    "total_leads": total_leads,
                    "qualified_leads": qualified_leads,
                    "consultations": consultations,
                    "conversions": conversions,
                    "total_spend": total_spend,
                    "avg_cpl": avg_cpl,
                    "consultation_rate": consultation_rate,
                    "conversion_rate": conversion_rate,
                    "cac": cac,
                    "recent_leads_count": last_7_count,
                    "leads_by_source": leads_by_source,
                    "status_breakdown": status_breakdown,
                    "trend": {"leads": last_7_count - prev_7_count, "percentage": trend_pct},
                    "pending_proposals": pending_proposals,
                },
            }
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {e}")
            return {"success": False, "error": str(e)}
        finally:
            session.close()

    def health_check(self) -> Dict[str, Any]:
        """Check health of core agents."""
        results = {}
        results["lead_capture"] = self.lead_capture.health_check()
        results["lead_scoring"] = self.lead_scoring.health_check()
        return {"healthy": all(r.get("healthy") for r in results.values()), "agents": results}
