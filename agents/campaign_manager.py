"""
Campaign Manager Agent (LLM + Automation).
Assembles full campaigns: targeting, ad groups, keywords, budget, schedule.
Creates campaign proposals that, once approved, can be pushed to Google/Facebook APIs.
"""

from typing import Any, Dict

from agents.base_agent import BaseAgent
from models.proposal import Proposal
from services.database import get_session
from services.openai_service import OpenAIService
from prompts import load_prompt


class CampaignManagerAgent(BaseAgent):
    """Creates detailed campaign proposals."""

    def __init__(self):
        super().__init__(name="CampaignManager")
        self.ai = OpenAIService()

    def run(self, platform: str = "google", goal: str = "lead generation", budget: int = None, **kwargs) -> Dict[str, Any]:
        """Create a campaign proposal for the specified platform."""
        if budget is None:
            budget = self.config.BUDGET_GOOGLE_ADS if platform == "google" else self.config.BUDGET_FACEBOOK

        if self.ai.is_available():
            campaign = self._ai_create(platform, goal, budget)
        else:
            campaign = self._default_campaign(platform, budget)

        session = get_session()
        try:
            proposal = Proposal(
                agent_name="CampaignManager",
                proposal_type="campaign",
                title=f"קמפיין: {campaign.get('campaign_name', platform)}",
                summary=f"קמפיין {platform} - {goal} - ₪{budget}/חודש",
                content=campaign,
                status="pending_review",
            )
            session.add(proposal)
            session.commit()
            self.logger.info(f"Campaign proposal created: {proposal.id}")
            return {"success": True, "proposal_id": proposal.id, "campaign": campaign}
        except Exception as e:
            session.rollback()
            return {"success": False, "errors": [str(e)]}
        finally:
            session.close()

    def _ai_create(self, platform: str, goal: str, budget: int) -> dict:
        from services.agent_memory import memory_service
        memory_ctx = memory_service.get_prompt_context("CampaignManager")
        prompt = load_prompt("campaign_manager", "system").format(platform=platform, budget=budget, goal=goal, memory_context=memory_ctx)
        result = self.ai.chat_json(system_prompt=prompt, user_message=f"Create the {platform} campaign now.", temperature=0.4, max_tokens=2000)
        return result or self._default_campaign(platform, budget)

    def _default_campaign(self, platform: str, budget: int) -> dict:
        if platform == "google":
            return {
                "campaign_name": "עיצוב פנים - חיפוש גוגל",
                "platform": "google",
                "objective": "Lead generation via search",
                "targeting": {"locations": ["הרצליה", "תל אביב", "רמת השרון", "כפר שמריהו", "סביון"], "age_min": 35, "age_max": 55, "interests": [], "languages": ["Hebrew"]},
                "ad_groups": [
                    {"name": "עיצוב פנים כללי", "keywords": ["עיצוב פנים הרצליה", "מעצבת פנים", "עיצוב פנים בתים פרטיים"], "match_type": "phrase", "bid_strategy": "maximize conversions", "daily_budget_nis": round(budget / 30, 1)},
                ],
                "ad_copy": [
                    {"headline1": "עיצוב פנים יוקרתי", "headline2": "אופיר אסולין | ייעוץ חינם", "description": "מתמחה בעיצוב וילות ובתים פרטיים באזור המרכז. קבעו שיחת ייעוץ חינמית.", "cta": "Book Consultation"},
                ],
                "schedule": {"start_date": "Next Monday", "days_of_week": ["Sun", "Mon", "Tue", "Wed", "Thu"], "hours": "08:00-22:00"},
                "estimated_metrics": {"daily_impressions": 80, "daily_clicks": 3, "estimated_cpl": round(budget / 3, 0)},
            }
        else:
            return {
                "campaign_name": "עיצוב פנים - לידים פייסבוק",
                "platform": "facebook",
                "objective": "Lead generation with native forms",
                "targeting": {"locations": ["Central Israel"], "age_min": 35, "age_max": 55, "interests": ["Interior design", "Luxury real estate", "Architecture"], "languages": ["Hebrew"]},
                "ad_groups": [{"name": "Lead Gen Main", "keywords": [], "match_type": "n/a", "bid_strategy": "lowest cost per lead", "daily_budget_nis": round(budget / 30, 1)}],
                "ad_copy": [{"headline1": "ייעוץ עיצוב פנים חינמי", "headline2": "", "description": "בונים בית חדש? אופיר אסולין מלווה פרויקטים מהתכנון ועד ההלבשה הסופית.", "cta": "Sign Up"}],
                "schedule": {"start_date": "Next Monday", "days_of_week": ["All"], "hours": "All day"},
                "estimated_metrics": {"daily_impressions": 300, "daily_clicks": 4, "estimated_cpl": round(budget / 2, 0)},
            }

    def health_check(self) -> Dict[str, Any]:
        return {"healthy": True, "ai_available": self.ai.is_available()}
