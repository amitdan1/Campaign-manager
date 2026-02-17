"""
Interaction history model.
Logs every touchpoint with a lead (email sent, WhatsApp message, call, etc.).
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from services.database import Base


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lead_id = Column(String(50), ForeignKey("leads.id"), nullable=False)
    channel = Column(String(50), nullable=False)  # email, whatsapp, phone, website, manual
    interaction_type = Column(String(100), nullable=False)  # welcome_email, followup_1, score_update, status_change, etc.
    content = Column(Text, nullable=True)  # Message body or description
    status = Column(String(50), default="sent")  # sent, delivered, opened, clicked, failed
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "lead_id": self.lead_id,
            "channel": self.channel,
            "interaction_type": self.interaction_type,
            "content": self.content,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Interaction lead={self.lead_id} type={self.interaction_type}>"
