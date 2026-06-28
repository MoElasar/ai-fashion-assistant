"""
Schedule schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List

from schemas.outfit import OutfitItemDetail


# =============================================================================
# REQUEST SCHEMAS
# =============================================================================

class ScheduleCreateRequest(BaseModel):
    """Request to schedule an outfit."""
    outfit_id: int
    scheduled_date: date
    notes: Optional[str] = Field(None, max_length=255)


class ScheduleUpdateRequest(BaseModel):
    """Request to update a scheduled outfit."""
    scheduled_date: Optional[date] = None
    notes: Optional[str] = None


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================

class ScheduledOutfitResponse(BaseModel):
    """Response for a scheduled outfit."""
    id: int
    user_id: int
    outfit_id: int
    scheduled_date: date
    notes: Optional[str] = None
    is_worn: bool = False
    created_at: datetime
    outfit_name: Optional[str] = None
    outfit_items: List[OutfitItemDetail] = []
    
    class Config:
        from_attributes = True


class WeekScheduleDay(BaseModel):
    """Single day in week schedule."""
    date: date
    day_name: str
    is_today: bool = False
    weather_forecast: Optional[dict] = None
    scheduled_outfit: Optional[ScheduledOutfitResponse] = None


class WeekScheduleResponse(BaseModel):
    """Response for week schedule view."""
    week: List[WeekScheduleDay]
    start_date: date
    end_date: date