"""
Outfit and OutfitItem models for outfit management.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


class Outfit(Base):
    """Saved outfit combination."""
    __tablename__ = "outfits"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    name = Column(String(100), nullable=True)  # Optional outfit name
    occasion = Column(String(50), nullable=True)  # casual, formal, sport, etc.
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="outfits")
    items = relationship("OutfitItem", back_populates="outfit", cascade="all, delete-orphan")
    scheduled_outfits = relationship("ScheduledOutfit", back_populates="outfit", cascade="all, delete-orphan")
    usage_history = relationship("UsageHistory", back_populates="outfit", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Outfit(id={self.id}, name={self.name}, occasion={self.occasion})>"


class OutfitItem(Base):
    """Junction table linking outfits to clothing items."""
    __tablename__ = "outfit_items"
    
    id = Column(Integer, primary_key=True, index=True)
    outfit_id = Column(Integer, ForeignKey("outfits.id"), nullable=False)
    clothing_item_id = Column(Integer, ForeignKey("clothing_items.id"), nullable=False)
    
    # Relationships
    outfit = relationship("Outfit", back_populates="items")
    clothing_item = relationship("ClothingItem", back_populates="outfit_items")
    
    def __repr__(self):
        return f"<OutfitItem(outfit_id={self.outfit_id}, clothing_item_id={self.clothing_item_id})>"