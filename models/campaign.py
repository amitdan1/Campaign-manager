"""
Campaign metrics database model.
Stores performance data pulled from ad platforms.
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Index
from services.database import Base


class Campaign(Base):
    __tablename__ = "campaigns"
    __table_args__ = (
        Index("ix_campaigns_campaign_id", "campaign_id"),
        Index("ix_campaigns_platform", "platform"),
        Index("ix_campaigns_date", "date"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(String(100), nullable=False)
    campaign_name = Column(String(300), nullable=False)
    platform = Column(String(50), nullable=False)  # google, facebook, instagram
    date = Column(DateTime, default=datetime.utcnow)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    cpl = Column(Float, default=0.0)  # Cost per lead
    ctr = Column(Float, default=0.0)  # Click-through rate %
    conversion_rate = Column(Float, default=0.0)  # Conversion rate %

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "campaign_id": self.campaign_id,
            "campaign_name": self.campaign_name,
            "platform": self.platform,
            "date": self.date.isoformat() if self.date else None,
            "impressions": self.impressions,
            "clicks": self.clicks,
            "conversions": self.conversions,
            "cost": self.cost,
            "cpl": self.cpl,
            "ctr": self.ctr,
            "conversion_rate": self.conversion_rate,
        }

    def __repr__(self):
        return f"<Campaign {self.campaign_name} platform={self.platform}>"
