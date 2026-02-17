"""
Agent Memory Service -- RAMP-inspired memory system for agents.
- Episodic: What did the agent do? What was approved/rejected?
- Semantic: Learned preferences (e.g., "user prefers conservative tone")
- Feedback: Direct user feedback on proposals
"""

import logging
from typing import Dict, Any, List, Optional

from services.database import get_session
from models.agent_memory import AgentMemory

logger = logging.getLogger("services.memory")


class MemoryService:
    """Read/write agent memories to improve agent output over time."""

    def store(
        self,
        agent_name: str,
        memory_type: str,
        key: str,
        value: Any,
        context: str = "",
    ) -> Optional[int]:
        """Store a memory. Returns the memory id."""
        session = get_session()
        try:
            mem = AgentMemory(
                agent_name=agent_name,
                memory_type=memory_type,
                key=key,
                value=value,
                context=context,
            )
            session.add(mem)
            session.commit()
            return mem.id
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to store memory: {e}")
            return None
        finally:
            session.close()

    def recall(
        self,
        agent_name: str,
        memory_type: str = None,
        key: str = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Recall memories for an agent, optionally filtered by type and key."""
        session = get_session()
        try:
            q = session.query(AgentMemory).filter(AgentMemory.agent_name == agent_name)
            if memory_type:
                q = q.filter(AgentMemory.memory_type == memory_type)
            if key:
                q = q.filter(AgentMemory.key == key)
            q = q.order_by(AgentMemory.created_at.desc()).limit(limit)
            return [m.to_dict() for m in q.all()]
        except Exception as e:
            logger.error(f"Failed to recall memories: {e}")
            return []
        finally:
            session.close()

    def get_prompt_context(self, agent_name: str, max_memories: int = 5) -> str:
        """
        Build a prompt-injectable context string from recent memories.
        This is injected into agent system prompts to give them memory.
        """
        memories = self.recall(agent_name, limit=max_memories)
        if not memories:
            return ""

        lines = ["## Past Experience (from your memory)"]
        for m in memories:
            mtype = m["memory_type"]
            key = m["key"]
            val = m["value"]
            if mtype == "feedback":
                lines.append(f"- User feedback on {key}: {val}")
            elif mtype == "episodic":
                lines.append(f"- Previous action ({key}): {val}")
            elif mtype == "semantic":
                lines.append(f"- Learned: {key} = {val}")
        return "\n".join(lines)

    def record_proposal_outcome(
        self,
        agent_name: str,
        proposal_title: str,
        status: str,
        feedback: str = "",
    ):
        """Record what happened to a proposal (approved, rejected, etc.)."""
        value = {"title": proposal_title, "outcome": status}
        if feedback:
            value["feedback"] = feedback

        key = f"proposal_{status}"
        self.store(agent_name, "episodic", key, value, context=feedback)

        # If rejected with feedback, also store as semantic memory
        if status == "rejected" and feedback:
            self.store(
                agent_name, "feedback", "rejection_reason",
                {"title": proposal_title, "reason": feedback},
                context=f"User rejected '{proposal_title}': {feedback}",
            )

    def record_preference(self, agent_name: str, preference_key: str, preference_value: Any):
        """Store a learned user preference."""
        self.store(agent_name, "semantic", preference_key, preference_value)

    def record_campaign_performance(
        self,
        agent_name: str,
        campaign_name: str,
        platform: str,
        metrics: Dict[str, Any],
    ):
        """
        Record campaign performance data so content agents can learn
        what works and what doesn't (closed-loop optimization).
        """
        value = {
            "campaign": campaign_name,
            "platform": platform,
            **metrics,
        }
        self.store(
            agent_name, "episodic", f"campaign_performance_{platform}",
            value,
            context=f"Campaign '{campaign_name}' on {platform}: CTR={metrics.get('ctr', 0):.1f}%, CPL=₪{metrics.get('cpl', 0):.0f}",
        )

    def get_performance_context(self, agent_name: str, max_records: int = 5) -> str:
        """
        Build a prompt-injectable performance summary from campaign memories.
        Used by Content and Landing Page agents for closed-loop optimization.
        """
        memories = self.recall(agent_name, memory_type="episodic", limit=max_records * 2)
        perf_memories = [m for m in memories if m["key"].startswith("campaign_performance_")]

        if not perf_memories:
            return ""

        lines = ["## Campaign Performance Data (learn from these results)"]

        top = sorted(perf_memories, key=lambda m: m["value"].get("ctr", 0), reverse=True)[:3]
        if top:
            lines.append("### Top Performing:")
            for m in top:
                v = m["value"]
                lines.append(
                    f"- {v.get('campaign', 'Unknown')} ({v.get('platform', '')}): "
                    f"CTR={v.get('ctr', 0):.1f}%, CPL=₪{v.get('cpl', 0):.0f}, "
                    f"Conv Rate={v.get('conversion_rate', 0):.1f}%"
                )

        bottom = sorted(perf_memories, key=lambda m: m["value"].get("ctr", 0))[:2]
        if bottom and bottom != top[:2]:
            lines.append("### Underperforming (avoid this style):")
            for m in bottom:
                v = m["value"]
                lines.append(
                    f"- {v.get('campaign', 'Unknown')} ({v.get('platform', '')}): "
                    f"CTR={v.get('ctr', 0):.1f}%, CPL=₪{v.get('cpl', 0):.0f}"
                )

        lines.append("")
        lines.append("Use these insights: build on what worked, avoid what didn't.")
        return "\n".join(lines)


# Singleton
memory_service = MemoryService()
