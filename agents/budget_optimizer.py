"""
Budget Optimizer Agent (LLM-powered).
Monitors spend vs performance and creates budget reallocation proposals.
Replaces the old OptimizationAgent with proposal-driven output.
"""

from datetime import datetime, timedelta
from typing import Any, Dict

from agents.base_agent import BaseAgent
from models.proposal import Proposal
from models.lead import Lead
from models.campaign import Campaign
from services.database import get_session
from services.openai_service import OpenAIService
from prompts import load_prompt


class BudgetOptimizerAgent(BaseAgent):
    """Analyzes spend and creates budget reallocation proposals."""

    def __init__(self):
        super().__init__(name="BudgetOptimizer")
        self.ai = OpenAIService()

    def run(self, days: int = 30, **kwargs) -> Dict[str, Any]:
        """Analyze budget and create optimization proposal."""
        perf = self._gather_performance(days)

        if self.ai.is_available():
            analysis = self._ai_analyze(perf)
        else:
            analysis = self._rule_analyze(perf)

        session = get_session()
        try:
            proposal = Proposal(
                agent_name="BudgetOptimizer",
                proposal_type="budget",
                title="אופטימיזציית תקציב",
                summary=analysis.get("assessment", ""),
                content=analysis,
                status="pending_review",
            )
            session.add(proposal)
            session.commit()
            self.logger.info(f"Budget proposal created: {proposal.id}")
            return {"success": True, "proposal_id": proposal.id, "analysis": analysis}
        except Exception as e:
            session.rollback()
            return {"success": False, "errors": [str(e)]}
        finally:
            session.close()

    def _ai_analyze(self, perf: str) -> dict:
        from services.agent_memory import memory_service
        memory_ctx = memory_service.get_prompt_context("BudgetOptimizer")
        prompt = load_prompt("budget_optimizer", "system").format(
            budget=self.config.BUDGET_TOTAL,
            google=self.config.BUDGET_GOOGLE_ADS,
            facebook=self.config.BUDGET_FACEBOOK,
            performance=perf,
            memory_context=memory_ctx,
        )
        result = self.ai.chat_json(system_prompt=prompt, user_message="Analyze and recommend budget changes.", temperature=0.3)
        return result or self._rule_analyze(perf)

    def _rule_analyze(self, perf: str) -> dict:
        return {
            "assessment": f"ניתוח תקציב בסיסי: תקציב חודשי ₪{self.config.BUDGET_TOTAL}. {perf}",
            "current_allocation": {"google": self.config.BUDGET_GOOGLE_ADS, "facebook": self.config.BUDGET_FACEBOOK},
            "recommended_allocation": {"google": self.config.BUDGET_GOOGLE_ADS, "facebook": self.config.BUDGET_FACEBOOK},
            "changes": [{"action": "maintain", "target": "All campaigns", "amount_nis": 0, "reason": "Insufficient data for changes. Continue monitoring."}],
            "expected_improvement": "Need more data to project improvements. Run campaigns for at least 2 weeks.",
        }

    def _gather_performance(self, days: int) -> str:
        from sqlalchemy import func

        session = get_session()
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)
            cutoff_prev = datetime.utcnow() - timedelta(days=days * 2)

            # Current period leads
            total_leads = session.query(func.count(Lead.id)).filter(Lead.created_at >= cutoff).scalar() or 0
            qualified_leads = session.query(func.count(Lead.id)).filter(
                Lead.created_at >= cutoff, Lead.quality_score >= 7
            ).scalar() or 0

            # Downstream conversions (consultation + converted)
            consultations = session.query(func.count(Lead.id)).filter(
                Lead.created_at >= cutoff, Lead.status == "consultation_booked"
            ).scalar() or 0
            converted = session.query(func.count(Lead.id)).filter(
                Lead.created_at >= cutoff, Lead.status == "converted"
            ).scalar() or 0

            # Leads by source
            source_rows = session.query(
                Lead.source, func.count(Lead.id)
            ).filter(Lead.created_at >= cutoff).group_by(Lead.source).all()
            leads_by_source = {row[0]: row[1] for row in source_rows}

            # Campaign metrics by platform
            platform_stats = session.query(
                Campaign.platform,
                func.sum(Campaign.cost).label("cost"),
                func.sum(Campaign.clicks).label("clicks"),
                func.sum(Campaign.impressions).label("impressions"),
                func.sum(Campaign.conversions).label("conversions"),
            ).filter(Campaign.date >= cutoff).group_by(Campaign.platform).all()

            # Previous period for trend comparison
            prev_leads = session.query(func.count(Lead.id)).filter(
                Lead.created_at >= cutoff_prev, Lead.created_at < cutoff
            ).scalar() or 0

            # Build structured report
            lines = [
                f"## Performance Summary (last {days} days)",
                f"",
                f"### Lead Metrics",
                f"| Metric | Value |",
                f"|--------|-------|",
                f"| Total Leads | {total_leads} |",
                f"| Qualified (score 7+) | {qualified_leads} |",
                f"| Consultations Booked | {consultations} |",
                f"| Converted (closed) | {converted} |",
                f"| Previous Period Leads | {prev_leads} |",
                f"| Trend | {'↑' if total_leads > prev_leads else '↓'} {abs(total_leads - prev_leads)} |",
                f"",
                f"### Leads by Source",
            ]
            for source, count in leads_by_source.items():
                lines.append(f"- {source}: {count} leads")

            lines.append("")
            lines.append("### Campaign Performance by Platform")
            lines.append("| Platform | Spend | Clicks | Impressions | Conversions | CTR | CPL | Conv Rate |")
            lines.append("|----------|-------|--------|-------------|-------------|-----|-----|-----------|")

            total_spend = 0
            for stat in platform_stats:
                plat, cost, clicks, impressions, conversions = stat
                cost = float(cost or 0)
                clicks = int(clicks or 0)
                impressions = int(impressions or 0)
                conversions = int(conversions or 0)
                total_spend += cost

                ctr = (clicks / impressions * 100) if impressions > 0 else 0
                cpl = (cost / conversions) if conversions > 0 else 0
                conv_rate = (conversions / clicks * 100) if clicks > 0 else 0

                lines.append(
                    f"| {plat} | ₪{cost:.0f} | {clicks} | {impressions} | {conversions} | "
                    f"{ctr:.1f}% | ₪{cpl:.0f} | {conv_rate:.1f}% |"
                )

            lines.append("")
            lines.append(f"### Budget Utilization")
            lines.append(f"- Total spend: ₪{total_spend:.0f} of ₪{self.config.BUDGET_TOTAL} monthly budget")
            lines.append(f"- Utilization: {(total_spend / self.config.BUDGET_TOTAL * 100):.0f}%" if self.config.BUDGET_TOTAL > 0 else "- No budget set")

            if consultations > 0 and total_spend > 0:
                cost_per_consultation = total_spend / consultations
                lines.append(f"- Cost per consultation: ₪{cost_per_consultation:.0f}")
            if converted > 0 and total_spend > 0:
                cac = total_spend / converted
                lines.append(f"- Customer Acquisition Cost: ₪{cac:.0f}")

            return "\n".join(lines)
        except Exception as e:
            self.logger.error(f"Error gathering performance: {e}")
            return "No performance data available yet."
        finally:
            session.close()

    def health_check(self) -> Dict[str, Any]:
        return {"healthy": True, "ai_available": self.ai.is_available()}
