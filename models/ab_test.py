"""
A/B Test model for tracking landing page variant performance.
"""

import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from services.database import Base


class ABTest(Base):
    __tablename__ = "ab_tests"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    status = Column(String(20), default="active")  # active, paused, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
        }


class ABTestVariant(Base):
    __tablename__ = "ab_test_variants"

    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, nullable=False, index=True)
    proposal_id = Column(Integer, nullable=False)
    variant_name = Column(String(100), nullable=False)  # e.g., "A", "B", "hero_gallery"
    weight = Column(Float, default=0.5)  # traffic allocation percentage
    views = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    @property
    def conversion_rate(self):
        return (self.conversions / self.views * 100) if self.views > 0 else 0.0

    def to_dict(self):
        return {
            "id": self.id,
            "test_id": self.test_id,
            "proposal_id": self.proposal_id,
            "variant_name": self.variant_name,
            "weight": self.weight,
            "views": self.views,
            "conversions": self.conversions,
            "conversion_rate": round(self.conversion_rate, 2),
        }
