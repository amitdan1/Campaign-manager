"""
Agent Memory model -- stores episodic and semantic memories across agent runs.
Enables agents to learn from past proposals, approvals, and rejections.
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, Index
from services.database import Base


class AgentMemory(Base):
    __tablename__ = "agent_memories"
    __table_args__ = (
        Index("ix_agent_memories_agent", "agent_name"),
        Index("ix_agent_memories_type", "memory_type"),
        Index("ix_agent_memories_key", "key"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_name = Column(String(100), nullable=False)
    memory_type = Column(String(50), nullable=False)  # episodic, semantic, feedback
    key = Column(String(200), nullable=False)  # e.g. "proposal_rejected", "user_preference"
    value = Column(JSON, nullable=True)  # The actual memory content
    context = Column(Text, nullable=True)  # Additional context
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "agent_name": self.agent_name,
            "memory_type": self.memory_type,
            "key": self.key,
            "value": self.value,
            "context": self.context,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<AgentMemory {self.agent_name}:{self.key}>"
