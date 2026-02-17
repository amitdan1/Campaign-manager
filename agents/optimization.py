"""
Optimization Agent -- now a thin wrapper around BudgetOptimizerAgent.
B6: All optimization output goes through the proposal system.
Kept for backward-compatibility with existing API endpoints.
"""

from typing import Any, Dict
from agents.budget_optimizer import BudgetOptimizerAgent


class OptimizationAgent(BudgetOptimizerAgent):
    """
    Legacy optimization agent. Delegates everything to BudgetOptimizerAgent
    so all output goes through the proposal workflow.
    """

    def __init__(self):
        super().__init__()
        self.agent_name = "Optimization"

    def run(self, days: int = 30, **kwargs) -> Dict[str, Any]:
        """Run budget optimizer and return in legacy format for /api/recommendations."""
        result = super().run(days=days, **kwargs)
        analysis = result.get("analysis", {})

        # Map to legacy format expected by the recommendations API
        recommendations = []
        for change in analysis.get("changes", []):
            recommendations.append({
                "action": change.get("action", "maintain"),
                "campaign": change.get("target", ""),
                "reason": change.get("reason", ""),
                "priority": "high" if change.get("amount_nis", 0) > 50 else "medium",
                "expected_impact": analysis.get("expected_improvement", ""),
            })

        return {
            "success": True,
            "proposal_id": result.get("proposal_id"),
            "overall_assessment": analysis.get("assessment", ""),
            "recommendations": recommendations,
            "budget_suggestion": str(analysis.get("recommended_allocation", {})),
            "data_summary": {},
        }

    def health_check(self) -> Dict[str, Any]:
        return {"healthy": True, "ai_available": self.ai.is_available(), "optimization_method": "proposal-based"}
