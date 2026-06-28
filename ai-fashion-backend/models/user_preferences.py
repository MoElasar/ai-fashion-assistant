"""
UserPreferences model for storing user settings.
Includes location for weather and preferred occasions.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


class UserPreferences(Base):
    """User preferences and settings."""
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Location for weather (coordinates)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    city_name = Column(String(100), nullable=True)  # For display purposes
    
    # Preferred occasions (comma-separated or JSON)
    preferred_occasions = Column(String(255), nullable=True)  # "casual,formal,sport"
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<UserPreferences(user_id={self.user_id}, city={self.city_name})>"