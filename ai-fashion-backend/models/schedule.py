"""
ScheduledOutfit model for weekly outfit planning.
"""

from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


class ScheduledOutfit(Base):
    """Outfit scheduled for a specific date."""
    __tablename__ = "scheduled_outfits"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    outfit_id = Column(Integer, ForeignKey("outfits.id"), nullable=False)
    
    scheduled_date = Column(Date, nullable=False)  # The date this outfit is planned for
    notes = Column(String(255), nullable=True)  # Optional notes: "Job interview", "Date night"
    is_worn = Column(Boolean, default=False)  # Whether the outfit was actually worn
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="scheduled_outfits")
    outfit = relationship("Outfit", back_populates="scheduled_outfits")
    
    def __repr__(self):
        return f"<ScheduledOutfit(id={self.id}, date={self.scheduled_date}, worn={self.is_worn})>"