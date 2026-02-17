"""
Strategy Agent (LLM-powered).
Reads the marketing strategy and creates weekly/monthly execution plans
as proposals. Decides which campaigns to run, content to create, and
how to allocate budget.
"""

from datetime import datetime
from typing import Any, Dict

from agents.base_agent import BaseAgent
from models.proposal import Proposal
from services.database import get_session
from services.openai_service import OpenAIService
from prompts import load_prompt


class StrategyAgent(BaseAgent):
    """Creates strategic marketing plans as proposals."""

    def __init__(self):
        super().__init__(name="Strategy")
        self.ai = OpenAIService()

    def run(self, **kwargs) -> Dict[str, Any]:
        """Generate a weekly strategy plan and save it as a proposal."""
        performance = self._get_performance_summary()

        if self.ai.is_available():
            plan = self._ai_plan(performance)
        else:
            plan = self._default_plan()

        # Save as proposal
        session = get_session()
        try:
            proposal = Proposal(
                agent_name="Strategy",
                proposal_type="strategy",
                title=plan.get("plan_title", "תוכנית שיווק שבועית"),
                summary=plan.get("summary", ""),
                content=plan,
                status="pending_review",
            )
            session.add(proposal)
            session.commit()
            proposal_id = proposal.id
            self.logger.info(f"Strategy proposal created: {proposal_id}")
            return {"success": True, "proposal_id": proposal_id, "plan": plan}
        except Exception as e:
            session.rollback()
            return {"success": False, "errors": [str(e)]}
        finally:
            session.close()

    def _ai_plan(self, performance: str) -> dict:
        from services.agent_memory import memory_service
        memory_ctx = memory_service.get_prompt_context("Strategy")

        segments_text = self._format_segments()

        prompt = load_prompt("strategy", "system").format(
            budget=self.config.BUDGET_TOTAL,
            google=self.config.BUDGET_GOOGLE_ADS,
            facebook=self.config.BUDGET_FACEBOOK,
            performance_data=performance,
            memory_context=memory_ctx,
        )
        prompt += f"\n\n{segments_text}"

        result = self.ai.chat_json(system_prompt=prompt, user_message="Create this week's marketing plan.", temperature=0.4, max_tokens=2000)
        return result or self._default_plan()

    def _format_segments(self) -> str:
        """Format service segments for the strategy prompt."""
        segments = self.config.SERVICE_SEGMENTS
        if not segments:
            return ""
        lines = [
            "## Audience Segments (plan campaigns per segment for better targeting)",
        ]
        for seg in segments:
            lines.append(
                f"- **{seg['name']}** ({seg['name_en']}): "
                f"Key message: {seg['key_message']}. "
                f"Keywords: {', '.join(seg['keywords'][:3])}. "
                f"Project types: {', '.join(seg['project_types'])}"
            )
        lines.append("")
        lines.append("Each campaign action should specify which segment it targets via a 'segment' field.")
        return "\n".join(lines)

    def _default_plan(self) -> dict:
        return {
            "plan_title": "תוכנית שיווק שבועית - ברירת מחדל",
            "summary": f"תוכנית בסיסית עם תקציב ₪{self.config.BUDGET_TOTAL} לחודש. מתמקדת בגוגל ופייסבוק עם טרגוט לפי פלחי קהל.",
            "actions": [
                {"type": "campaign", "title": "קמפיין חיפוש גוגל - וילות חדשות", "description": "קמפיין חיפוש ממוקד לבוני וילות חדשות באזור המרכז", "platform": "google", "budget_nis": int(self.config.BUDGET_GOOGLE_ADS * 0.5), "priority": "high", "expected_leads": 2, "segment": "villa_new_build"},
                {"type": "campaign", "title": "קמפיין חיפוש גוגל - שיפוצים", "description": "קמפיין חיפוש ממוקד למשפצים באזור הרצליה ותל אביב", "platform": "google", "budget_nis": int(self.config.BUDGET_GOOGLE_ADS * 0.5), "priority": "high", "expected_leads": 2, "segment": "renovation"},
                {"type": "campaign", "title": "קמפיין לידים פייסבוק - דירות יוקרה", "description": "קמפיין יצירת לידים לבעלי פנטהאוזים ודירות יוקרה", "platform": "facebook", "budget_nis": self.config.BUDGET_FACEBOOK, "priority": "high", "expected_leads": 2, "segment": "luxury_apartment"},
                {"type": "content", "title": "פוסטים לרשתות חברתיות", "description": "3 פוסטים שבועיים עם תמונות פרויקטים", "platform": "instagram", "budget_nis": 0, "priority": "medium", "expected_leads": 1},
                {"type": "landing_page", "title": "דף נחיתה - משפצים", "description": "דף נחיתה ממוקד למשפצים עם מדריך חינמי", "platform": "website", "budget_nis": 0, "priority": "medium", "expected_leads": 2, "segment": "renovation"},
            ],
            "budget_breakdown": {"google_ads": self.config.BUDGET_GOOGLE_ADS, "facebook": self.config.BUDGET_FACEBOOK, "other": 0},
        }

    def _get_performance_summary(self) -> str:
        from models.lead import Lead
        from models.campaign import Campaign
        from datetime import timedelta
        session = get_session()
        try:
            cutoff = datetime.utcnow() - timedelta(days=30)
            leads = session.query(Lead).filter(Lead.created_at >= cutoff).count()
            campaigns = session.query(Campaign).filter(Campaign.date >= cutoff).all()
            spend = sum(c.cost for c in campaigns)
            conv = sum(c.conversions for c in campaigns)
            return f"Last 30 days: {leads} leads, ₪{spend:.0f} spent, {conv} conversions."
        except Exception:
            return "No performance data available yet."
        finally:
            session.close()

    def health_check(self) -> Dict[str, Any]:
        return {"healthy": True, "ai_available": self.ai.is_available()}
