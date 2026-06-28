"""
UsageHistory model for tracking when clothing items are worn.
Used for analytics and recommendations.
"""

from sqlalchemy import Column, Integer, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


class UsageHistory(Base):
    """Tracks each time a clothing item is worn."""
    __tablename__ = "usage_history"
    
    id = Column(Integer, primary_key=True, index=True)
    clothing_item_id = Column(Integer, ForeignKey("clothing_items.id"), nullable=False)
    outfit_id = Column(Integer, ForeignKey("outfits.id"), nullable=True)  # Optional link to outfit
    
    worn_date = Column(Date, nullable=False)  # The date the item was worn
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    clothing_item = relationship("ClothingItem", back_populates="usage_history")
    outfit = relationship("Outfit", back_populates="usage_history")
    
    def __repr__(self):
        return f"<UsageHistory(item_id={self.clothing_item_id}, date={self.worn_date})>"