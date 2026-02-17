"""
BrandAsset model -- scraped content library.
Stores images, text, and style elements from Ofir's digital presence.
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, JSON, Index
from services.database import Base


class BrandAsset(Base):
    __tablename__ = "brand_assets"
    __table_args__ = (
        Index("ix_brand_assets_source", "source"),
        Index("ix_brand_assets_type", "asset_type"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_type = Column(String(50), nullable=False)  # image, text, color, font, video
    source = Column(String(50), nullable=False)  # website, instagram, facebook, tiktok
    url = Column(String(500), nullable=False)
    local_path = Column(String(500), nullable=True)
    thumbnail_path = Column(String(500), nullable=True)
    asset_metadata = Column(JSON, nullable=True)  # alt text, caption, hashtags, dimensions, etc.
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "asset_type": self.asset_type,
            "source": self.source,
            "url": self.url,
            "local_path": self.local_path,
            "thumbnail_path": self.thumbnail_path,
            "metadata": self.asset_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<BrandAsset {self.id} {self.asset_type} from {self.source}>"
