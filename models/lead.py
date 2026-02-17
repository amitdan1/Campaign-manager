"""
Lead database model.
Stores all captured leads and their qualification data.
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Index
from services.database import Base


class Lead(Base):
    __tablename__ = "leads"
    __table_args__ = (
        Index("ix_leads_email", "email"),
        Index("ix_leads_phone", "phone"),
        Index("ix_leads_status", "status"),
        Index("ix_leads_source", "source"),
        Index("ix_leads_created_at", "created_at"),
    )

    id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    phone = Column(String(50), nullable=False)
    email = Column(String(200), nullable=False)
    source = Column(String(50), nullable=False)  # google, facebook, instagram, organic, website
    campaign = Column(String(200), default="")
    status = Column(String(50), default="new")  # new, contacted, qualified, consultation_booked, converted, lost
    quality_score = Column(Integer, nullable=True)  # 1-10
    score_reasoning = Column(Text, nullable=True)  # AI explanation for the score
    location = Column(String(200), nullable=True)
    budget = Column(String(100), nullable=True)
    project_type = Column(String(100), nullable=True)  # new_build, renovation, commercial
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "source": self.source,
            "campaign": self.campaign,
            "status": self.status,
            "quality_score": self.quality_score,
            "score_reasoning": self.score_reasoning,
            "location": self.location,
            "budget": self.budget,
            "project_type": self.project_type,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Lead {self.id} name={self.name} score={self.quality_score}>"
