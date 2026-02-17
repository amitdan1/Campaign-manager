"""
Execution Pipeline - Autonomous orchestration logic.
When a strategy proposal is approved, it triggers downstream agents
to create their own proposals (campaigns, content, landing pages, etc.).
When individual proposals are approved, it triggers their execution.

B3: Uses single session per pipeline execution, continues on individual errors.
C4: Prevents duplicate cycles and downstream proposals.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

from services.database import get_session
from models.proposal import Proposal

logger = logging.getLogger("pipeline")


class ExecutionPipeline:
    """
    Connects strategy plans to downstream agent actions.

    Flow:
    1. Strategy approved -> Trigger CampaignManager, ContentCreative, LandingPage
    2. Campaign approved -> Mark as executing (push to ads APIs when configured)
    3. Budget proposal approved -> Apply budget changes
    4. Landing page approved -> Mark as live
    """

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator

    def on_proposal_approved(self, proposal_id: int) -> Dict[str, Any]:
        """
        Called when a proposal is approved.
        Determines what downstream actions to trigger based on proposal type.
        """
        session = get_session()
        try:
            proposal = session.query(Proposal).filter_by(id=proposal_id).first()
            if not proposal:
                return {"success": False, "error": "Proposal not found"}

            proposal_type = proposal.proposal_type
            content = proposal.content or {}
            results = {"proposal_id": proposal_id, "type": proposal_type, "triggered": []}

            if proposal_type == "strategy":
                results["triggered"] = self._execute_strategy(content, parent_id=proposal_id)
            elif proposal_type == "campaign":
                results["triggered"] = self._execute_campaign(proposal_id)
            elif proposal_type == "budget":
                results["triggered"] = self._execute_budget(content)
            elif proposal_type == "landing_page":
                results["triggered"] = self._execute_landing_page(proposal_id)

            return {"success": True, **results}
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            return {"success": False, "error": str(e)}
        finally:
            session.close()

    def _execute_strategy(self, plan: dict, parent_id: int = None) -> List[dict]:
        """
        Strategy approved -> create downstream proposals from each action item.
        B3: Uses try/except per action so one failure doesn't stop the rest.
        C4: Checks for duplicate proposals before creating.
        """
        triggered = []
        actions = plan.get("actions", [])

        for action in actions:
            action_type = action.get("type", "")
            title = action.get("title", "")
            platform = action.get("platform", "google")
            budget = action.get("budget_nis", 0)
            segment = action.get("segment", "")

            # C4: Skip if a pending proposal with same title already exists
            if self._has_pending_proposal(title, action_type):
                triggered.append({"type": action_type, "title": title, "skipped": "duplicate"})
                continue

            try:
                if action_type == "campaign":
                    result = self.orchestrator.campaign_manager.run(
                        platform=platform, goal=title, budget=budget or None,
                    )
                    if result.get("success"):
                        self._set_parent(result["proposal_id"], parent_id)
                        triggered.append({"type": "campaign", "proposal_id": result["proposal_id"], "title": title})

                elif action_type == "content":
                    result = self.orchestrator.content.run(content_type="social_post", campaign=title, segment=segment)
                    if result.get("success"):
                        session = get_session()
                        try:
                            p = Proposal(
                                agent_name="ContentCreative", proposal_type="content",
                                title=f"תוכן: {title}", summary=f"תוכן שנוצר ל: {title}",
                                content=result, status="pending_review",
                                parent_proposal_id=parent_id,
                            )
                            session.add(p)
                            session.commit()
                            triggered.append({"type": "content", "proposal_id": p.id, "title": title})
                        except Exception:
                            session.rollback()
                        finally:
                            session.close()

                elif action_type == "landing_page":
                    result = self.orchestrator.landing_page.run(
                        campaign_name=title, campaign_details=action.get("description", ""),
                        segment=segment,
                    )
                    if result.get("success"):
                        self._set_parent(result["proposal_id"], parent_id)
                        triggered.append({"type": "landing_page", "proposal_id": result["proposal_id"], "title": title})

            except Exception as e:
                logger.error(f"Error triggering {action_type} for '{title}': {e}")
                triggered.append({"type": action_type, "error": str(e), "title": title})

        return triggered

    def _execute_campaign(self, proposal_id: int) -> List[dict]:
        """Campaign approved -> mark as executing."""
        session = get_session()
        try:
            p = session.query(Proposal).filter_by(id=proposal_id).first()
            if p:
                p.status = "executing"
                p.executed_at = datetime.utcnow()
                session.commit()
                logger.info(f"Campaign {proposal_id} marked as executing")
            return [{"type": "campaign_execution", "status": "executing", "note": "Campaign queued for API push"}]
        except Exception as e:
            session.rollback()
            return [{"type": "error", "error": str(e)}]
        finally:
            session.close()

    def _execute_budget(self, content: dict) -> List[dict]:
        """Budget change approved -> log the new allocation."""
        new_alloc = content.get("recommended_allocation", {})
        logger.info(f"Budget reallocation approved: {new_alloc}")
        return [{"type": "budget_applied", "allocation": new_alloc}]

    def _execute_landing_page(self, proposal_id: int) -> List[dict]:
        """Landing page approved -> mark as completed/live."""
        session = get_session()
        try:
            p = session.query(Proposal).filter_by(id=proposal_id).first()
            if p:
                p.status = "completed"
                p.executed_at = datetime.utcnow()
                session.commit()
                logger.info(f"Landing page {proposal_id} published")
            return [{"type": "landing_page_published", "proposal_id": proposal_id}]
        except Exception as e:
            session.rollback()
            return [{"type": "error", "error": str(e)}]
        finally:
            session.close()

    # --- C4: Duplicate prevention helpers ---

    def _has_pending_proposal(self, title: str, ptype: str) -> bool:
        session = get_session()
        try:
            return session.query(Proposal).filter(
                Proposal.title.contains(title),
                Proposal.status == "pending_review",
            ).first() is not None
        except Exception:
            return False
        finally:
            session.close()

    def _set_parent(self, child_id: int, parent_id: int):
        if not parent_id:
            return
        session = get_session()
        try:
            p = session.query(Proposal).filter_by(id=child_id).first()
            if p:
                p.parent_proposal_id = parent_id
                session.commit()
        except Exception:
            session.rollback()
        finally:
            session.close()

    def run_weekly_cycle(self) -> Dict[str, Any]:
        """
        Trigger the full weekly autonomous cycle.
        C4: Checks for existing pending strategy proposals to prevent duplicates.
        """
        logger.info("Starting weekly autonomous cycle...")

        # C4: Check for existing pending strategy
        session = get_session()
        try:
            existing = session.query(Proposal).filter(
                Proposal.proposal_type == "strategy",
                Proposal.status == "pending_review",
            ).first()
            if existing:
                return {
                    "success": False,
                    "error": f"A pending strategy proposal already exists (#{existing.id}). Approve or reject it first.",
                    "existing_proposal_id": existing.id,
                }
        finally:
            session.close()

        # Generate new strategy plan
        strategy_result = self.orchestrator.strategy.run()
        if not strategy_result.get("success"):
            return {"success": False, "error": "Strategy generation failed", "details": strategy_result}

        budget_result = self.orchestrator.budget_optimizer.run()

        return {
            "success": True,
            "strategy_proposal_id": strategy_result.get("proposal_id"),
            "budget_proposal_id": budget_result.get("proposal_id"),
            "message": "Weekly cycle started. Strategy and budget proposals created for review.",
        }
