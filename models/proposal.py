"""
Proposal model -- core of the approval workflow.
Every significant agent action produces a Proposal that goes through
Draft -> PendingReview -> Approved/Rejected -> Executing -> Completed.
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, Index, ForeignKey
from services.database import Base


class Proposal(Base):
    __tablename__ = "proposals"
    __table_args__ = (
        Index("ix_proposals_status", "status"),
        Index("ix_proposals_type", "proposal_type"),
        Index("ix_proposals_agent", "agent_name"),
        Index("ix_proposals_created_at", "created_at"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_name = Column(String(100), nullable=False)
    proposal_type = Column(String(50), nullable=False)  # campaign, landing_page, ad_copy, budget, strategy, content
    title = Column(String(300), nullable=False)
    summary = Column(Text, nullable=True)
    content = Column(JSON, nullable=True)  # Full proposal data as JSON
    status = Column(String(50), default="pending_review")  # draft, pending_review, approved, revision_requested, rejected, executing, completed, failed
    feedback = Column(Text, nullable=True)  # User's revision comments
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)
    executed_at = Column(DateTime, nullable=True)
    parent_proposal_id = Column(Integer, nullable=True)  # FK to parent strategy proposal

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "agent_name": self.agent_name,
            "proposal_type": self.proposal_type,
            "title": self.title,
            "summary": self.summary,
            "content": self.content,
            "status": self.status,
            "feedback": self.feedback,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
            "parent_proposal_id": self.parent_proposal_id,
        }

    def __repr__(self):
        return f"<Proposal {self.id} '{self.title}' status={self.status}>"
