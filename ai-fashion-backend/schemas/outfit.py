"""
Outfit schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any


# =============================================================================
# REQUEST SCHEMAS
# =============================================================================

class OutfitCreateRequest(BaseModel):
    """Request to create/save an outfit."""
    name: Optional[str] = Field(None, max_length=100)
    occasion: Optional[str] = None
    item_ids: List[int] = Field(..., min_length=1, description="List of clothing item IDs")


class OutfitUpdateRequest(BaseModel):
    """Request to update an outfit."""
    name: Optional[str] = None
    occasion: Optional[str] = None


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================

class OutfitItemDetail(BaseModel):
    """Clothing item detail within an outfit."""
    id: int
    clothing_type: str
    layer_type: str
    image_path: str
    primary_color_hex: Optional[str] = None
    
    class Config:
        from_attributes = True


class OutfitResponse(BaseModel):
    """Response for a single outfit."""
    id: int
    user_id: int
    name: Optional[str] = None
    occasion: Optional[str] = None
    created_at: datetime
    items: List[OutfitItemDetail] = []
    
    class Config:
        from_attributes = True


class OutfitListResponse(BaseModel):
    """Response for list of outfits."""
    outfits: List[OutfitResponse]
    total: int