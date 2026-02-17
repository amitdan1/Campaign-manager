"""
ChatMessage model -- stores conversation history between user and agents.
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from services.database import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    role = Column(String(20), nullable=False)  # user, agent
    agent_name = Column(String(100), nullable=True)  # which agent responded
    content = Column(Text, nullable=False)
    proposal_id = Column(Integer, nullable=True)  # optional link to a proposal
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "role": self.role,
            "agent_name": self.agent_name,
            "content": self.content,
            "proposal_id": self.proposal_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<ChatMessage {self.id} role={self.role}>"
