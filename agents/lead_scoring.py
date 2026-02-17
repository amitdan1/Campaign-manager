"""
Lead Scoring Agent (LLM-powered).
Uses OpenAI to analyze lead context and produce a nuanced quality score
with human-readable reasoning, tailored to Ofir Assulin's ideal client profile.
Falls back to rule-based scoring when OpenAI is not configured.
"""

from datetime import datetime
from typing import Any, Dict

from agents.base_agent import BaseAgent
from models.lead import Lead
from models.interaction import Interaction
from services.database import get_session
from services.openai_service import OpenAIService
from prompts import load_prompt


class LeadScoringAgent(BaseAgent):
    """Scores leads using AI or rule-based fallback."""

    def __init__(self):
        super().__init__(name="LeadScoring")
        self.ai = OpenAIService()

    def run(self, lead_id: str = None, **kwargs) -> Dict[str, Any]:
        """
        Score a specific lead by ID, or score all unscored leads.
        """
        if lead_id:
            return self._score_lead(lead_id)
        return self._score_all_unscored()

    def _score_lead(self, lead_id: str) -> Dict[str, Any]:
        """Score a single lead."""
        session = get_session()
        try:
            lead = session.query(Lead).filter_by(id=lead_id).first()
            if not lead:
                return {"success": False, "errors": [f"Lead {lead_id} not found"]}

            if self.ai.is_available():
                result = self._ai_score(lead)
            else:
                result = self._rule_based_score(lead)

            lead.quality_score = result["score"]
            lead.score_reasoning = result["reasoning"]
            lead.updated_at = datetime.utcnow()

            # Log scoring interaction
            interaction = Interaction(
                lead_id=lead.id,
                channel="ai" if self.ai.is_available() else "system",
                interaction_type="lead_scored",
                content=f"Score: {result['score']}/10 - {result['reasoning']}",
                status="completed",
            )
            session.add(interaction)
            session.commit()

            self.logger.info(f"Lead {lead_id} scored: {result['score']}/10")
            return {
                "success": True,
                "lead_id": lead_id,
                "score": result["score"],
                "reasoning": result["reasoning"],
                "priority": result.get("priority", "medium"),
                "recommended_action": result.get("recommended_action", ""),
                "method": "ai" if self.ai.is_available() else "rules",
            }

        except Exception as e:
            session.rollback()
            self.logger.error(f"Error scoring lead {lead_id}: {e}")
            return {"success": False, "errors": [str(e)]}
        finally:
            session.close()

    def _score_all_unscored(self) -> Dict[str, Any]:
        """Score all leads that don't have a score yet."""
        session = get_session()
        try:
            unscored = session.query(Lead).filter(Lead.quality_score.is_(None)).all()
            lead_ids = [lead.id for lead in unscored]
        finally:
            session.close()

        results = []
        for lid in lead_ids:
            result = self._score_lead(lid)
            results.append(result)

        scored_count = sum(1 for r in results if r.get("success"))
        return {
            "success": True,
            "total_unscored": len(lead_ids),
            "scored": scored_count,
            "results": results,
        }

    def _ai_score(self, lead: Lead) -> dict:
        """Use OpenAI to score the lead."""
        user_message = (
            f"Score this lead:\n"
            f"- Name: {lead.name}\n"
            f"- Phone: {lead.phone}\n"
            f"- Email: {lead.email}\n"
            f"- Source: {lead.source}\n"
            f"- Campaign: {lead.campaign}\n"
            f"- Location: {lead.location or 'Not provided'}\n"
            f"- Budget: {lead.budget or 'Not provided'}\n"
            f"- Project Type: {lead.project_type or 'Not provided'}\n"
            f"- Notes: {lead.notes or 'None'}\n"
        )

        from services.agent_memory import memory_service
        memory_ctx = memory_service.get_prompt_context("LeadScoring")
        system_prompt = load_prompt("lead_scoring", "system").format(memory_context=memory_ctx)

        result = self.ai.chat_json(
            system_prompt=system_prompt,
            user_message=user_message,
            temperature=0.2,
        )

        if result and "score" in result:
            return {
                "score": max(1, min(10, int(result["score"]))),
                "reasoning": result.get("reasoning", "AI scored this lead."),
                "priority": result.get("priority", "medium"),
                "recommended_action": result.get("recommended_action", ""),
            }

        # Fallback if AI response was invalid
        self.logger.warning("AI scoring returned invalid result, falling back to rules")
        return self._rule_based_score(lead)

    def _rule_based_score(self, lead: Lead) -> dict:
        """Fallback: deterministic scoring based on rules."""
        score = 5  # Base score
        reasons = []

        # Location scoring
        target_locations = self.config.TARGET_LOCATIONS
        if lead.location:
            if any(loc in lead.location for loc in target_locations):
                score += 2
                reasons.append(f"Location '{lead.location}' is in target area")
            else:
                reasons.append(f"Location '{lead.location}' is outside target area")
        else:
            reasons.append("No location provided")

        # Budget scoring
        if lead.budget:
            try:
                budget_num = int(lead.budget.replace(",", "").replace("₪", "").strip())
                if budget_num >= self.config.TARGET_MIN_PROJECT_BUDGET:
                    score += 2
                    reasons.append(f"Budget ₪{budget_num:,} meets minimum")
                elif budget_num >= self.config.TARGET_MIN_PROJECT_BUDGET * 0.7:
                    score += 1
                    reasons.append(f"Budget ₪{budget_num:,} is close to minimum")
                else:
                    reasons.append(f"Budget ₪{budget_num:,} is below target")
            except ValueError:
                reasons.append("Could not parse budget")
        else:
            reasons.append("No budget provided")

        # Project type scoring + segment match
        if lead.project_type in ("new_build", "renovation", "villa"):
            score += 1
            reasons.append(f"Project type '{lead.project_type}' is high value")
        elif lead.project_type in ("penthouse", "luxury_apt"):
            score += 1
            reasons.append(f"Project type '{lead.project_type}' matches luxury segment")

        # Segment match bonus: lead from a campaign targeting their segment scores higher
        matched_segment = self.config.get_segment_for_project_type(lead.project_type)
        if matched_segment:
            reasons.append(f"Matches service segment: {matched_segment['name']}")

        # Source scoring
        if lead.source == "google":
            score += 1
            reasons.append("Google source indicates active search intent")
        elif lead.source in ("facebook", "instagram"):
            reasons.append("Social media source - moderate intent")

        score = max(1, min(10, score))
        priority = "high" if score >= 7 else ("medium" if score >= 5 else "low")

        return {
            "score": score,
            "reasoning": ". ".join(reasons) + ".",
            "priority": priority,
            "recommended_action": (
                "Contact immediately - high potential client"
                if priority == "high"
                else "Follow up within 24 hours" if priority == "medium"
                else "Add to nurture sequence"
            ),
        }

    def health_check(self) -> Dict[str, Any]:
        return {
            "healthy": True,
            "ai_available": self.ai.is_available(),
            "scoring_method": "ai" if self.ai.is_available() else "rule-based",
        }
