"""
ClothingItem model for wardrobe management.
Stores clothing details including AI-detected attributes.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


class ClothingItem(Base):
    """Individual clothing item in user's wardrobe."""
    __tablename__ = "clothing_items"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Image
    image_path = Column(String(500), nullable=False)
    
    # AI-detected fields (from Gemini Vision)
    clothing_type = Column(String(50), nullable=False)  # shirt, pants, jacket, etc.
    attributes = Column(Text, nullable=True)  # JSON string: ["denim", "casual", "cotton"]
    confidence_score = Column(Float, nullable=True)  # Detection confidence percentage
    
    # Color extraction (from K-Means)
    primary_color_hex = Column(String(7), nullable=True)  # #FFFFFF format
    secondary_color_hex = Column(String(7), nullable=True)
    
    # Layer category for outfit building
    layer_type = Column(String(20), nullable=False)  # top, bottom, outerwear, footwear, socks
    
    # Usage tracking for analytics
    times_worn = Column(Integer, default=0)
    last_worn_date = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="clothing_items")
    outfit_items = relationship("OutfitItem", back_populates="clothing_item", cascade="all, delete-orphan")
    usage_history = relationship("UsageHistory", back_populates="clothing_item", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ClothingItem(id={self.id}, type={self.clothing_type}, layer={self.layer_type})>"